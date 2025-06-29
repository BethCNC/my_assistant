from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import openai
import sqlite3
import traceback
import json
from datetime import datetime
from typing import List, Optional

# Import all services
try:
    from rag_service import (
        learn_from_conversation, 
        get_enhanced_response, 
        get_contextual_insights,
        get_rag_learning_stats
    )
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"RAG service not available: {e}")
    RAG_AVAILABLE = False

try:
    from memory import (
        create_conversation_session,
        add_conversation_message,
        get_conversation_messages,
        get_memory_statistics
    )
    MEMORY_AVAILABLE = True
except ImportError as e:
    print(f"Memory service not available: {e}")
    MEMORY_AVAILABLE = False

try:
    from notion import (
        search_notion,
        create_notion_task,
        get_recent_notion_tasks
    )
    NOTION_AVAILABLE = True
except ImportError as e:
    print(f"Notion service not available: {e}")
    NOTION_AVAILABLE = False

try:
    from github import (
        get_github_repos,
        get_recent_github_activity,
        create_github_issue
    )
    GITHUB_AVAILABLE = True
except ImportError as e:
    print(f"GitHub service not available: {e}")
    GITHUB_AVAILABLE = False

try:
    from figma import (
        get_figma_files,
        get_recent_figma_files
    )
    FIGMA_AVAILABLE = True
except ImportError as e:
    print(f"Figma service not available: {e}")
    FIGMA_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Beth Assistant API with RAG", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for deployment verification."""
    return {
        "message": "Beth Assistant API with RAG is running", 
        "status": "healthy",
        "services": {
            "rag": RAG_AVAILABLE,
            "memory": MEMORY_AVAILABLE,
            "notion": NOTION_AVAILABLE,
            "github": GITHUB_AVAILABLE,
            "figma": FIGMA_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "rag_enabled": RAG_AVAILABLE
    }

# Enhanced chat endpoint with RAG
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None

@app.post("/api/chat")
async def enhanced_chat_endpoint(chat_request: ChatMessage):
    """Enhanced chat endpoint with RAG learning and personalized responses."""
    try:
        conversation_id = chat_request.conversation_id or f"conv_{datetime.now().timestamp()}"
        
        # Create conversation if new
        if MEMORY_AVAILABLE:
            create_conversation_session(user_id="beth", title=f"Chat {datetime.now().strftime('%H:%M')}")
            
            # Add user message to memory
            add_conversation_message(
                conversation_id=conversation_id,
                role="user",
                content=chat_request.message,
                metadata=chat_request.context
            )
        
        # Generate enhanced response using RAG
        if RAG_AVAILABLE:
            rag_result = get_enhanced_response(
                query=chat_request.message,
                context=chat_request.context
            )
            
            if rag_result['success']:
                response_text = rag_result['response']
                
                # Add assistant response to memory
                if MEMORY_AVAILABLE:
                    add_conversation_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=response_text,
                        metadata={
                            "rag_enhanced": True,
                            "context_used": rag_result.get('context_used', 0),
                            "insights_applied": rag_result.get('insights_applied', [])
                        }
                    )
                
                # Learn from this conversation
                if MEMORY_AVAILABLE:
                    messages = get_conversation_messages(conversation_id)
                    if messages['success']:
                        learn_from_conversation(
                            conversation_id=conversation_id,
                            messages=messages['messages'],
                            context=chat_request.context
                        )
                
                return {
                    "response": response_text,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat(),
                    "rag_enhanced": True,
                    "learning_applied": True
                }
            else:
                # Fallback to simple response
                response_text = f"I understand you're asking about: {chat_request.message}. Let me help you with that."
        else:
            # Simple response without RAG
            response_text = f"I received your message: {chat_request.message}"
        
        return {
            "response": response_text,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "rag_enhanced": False
        }
        
    except Exception as e:
        return {
            "error": str(e), 
            "status": "error",
            "conversation_id": chat_request.conversation_id
        }

@app.get("/api/chats")
async def get_conversations():
    """Get list of conversations with learning insights."""
    try:
        if MEMORY_AVAILABLE:
            # Get real conversations from memory
            from memory import memory_service
            conversations = memory_service.get_recent_conversations(days=30, limit=20)
            
            if conversations['success']:
                return conversations['conversations']
        
        # Fallback to mock data
        mock_conversations = [
            {
                "id": "1",
                "title": "How can I better update my design tokens",
                "preview": "Discussion about design system tokens",
                "timestamp": datetime.now().isoformat(),
                "message_count": 5,
                "rag_enhanced": True
            },
            {
                "id": "2", 
                "title": "How can I better organize my projects",
                "preview": "Project organization strategies",
                "timestamp": datetime.now().isoformat(),
                "message_count": 8,
                "rag_enhanced": True
            }
        ]
        return mock_conversations
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/chats/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get chat history for a specific conversation."""
    try:
        if MEMORY_AVAILABLE:
            result = get_conversation_messages(conversation_id)
            if result['success']:
                return result['messages']
        
        # Fallback to mock data
        return [
            {
                "id": "1",
                "content": "How can I better update my design tokens?",
                "role": "user",
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conversation_id
            }
        ]
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

# RAG-specific endpoints
@app.get("/api/rag/insights")
async def get_learning_insights(query: str = "", limit: int = 5):
    """Get contextual insights based on learned patterns."""
    try:
        if not RAG_AVAILABLE:
            return {"error": "RAG service not available", "status": "error"}
        
        if query:
            insights = get_contextual_insights(query, limit)
        else:
            insights = get_rag_learning_stats()
        
        return insights
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/rag/stats")
async def get_learning_statistics():
    """Get statistics about what the system has learned."""
    try:
        if not RAG_AVAILABLE:
            return {"error": "RAG service not available", "status": "error"}
        
        return get_rag_learning_stats()
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

# Service-specific endpoints
@app.get("/api/notion/search")
async def search_notion_content(query: str, limit: int = 10):
    """Search Notion content."""
    try:
        if not NOTION_AVAILABLE:
            return {"error": "Notion service not available", "status": "error"}
        
        return search_notion(query, limit)
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/api/notion/task")
async def create_task(title: str, description: str = "", project: str = ""):
    """Create a new task in Notion."""
    try:
        if not NOTION_AVAILABLE:
            return {"error": "Notion service not available", "status": "error"}
        
        return create_notion_task(title, description, project)
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/github/repos")
async def get_repositories():
    """Get GitHub repositories."""
    try:
        if not GITHUB_AVAILABLE:
            return {"error": "GitHub service not available", "status": "error"}
        
        return get_github_repos()
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/figma/files")
async def get_design_files():
    """Get Figma design files."""
    try:
        if not FIGMA_AVAILABLE:
            return {"error": "Figma service not available", "status": "error"}
        
        return get_figma_files()
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/figma/variables/{file_key}")
async def get_figma_variables(file_key: str):
    """Get all variables from a Figma file."""
    try:
        if not FIGMA_AVAILABLE:
            return {"error": "Figma service not available", "status": "error"}
        
        from figma import figma_service
        return figma_service.get_file_variables(file_key)
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/figma/variables/{file_key}/documentation")
async def generate_figma_variables_documentation(file_key: str, format: str = "markdown"):
    """Generate comprehensive documentation for Figma variable collections."""
    try:
        if not FIGMA_AVAILABLE:
            return {"error": "Figma service not available", "status": "error"}
        
        from figma import figma_service
        result = figma_service.generate_variables_documentation(file_key, format)
        
        if result['success'] and format == "markdown":
            # Save the documentation to a file
            doc_filename = f"FIGMA_VARIABLES_DOCUMENTATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            try:
                with open(doc_filename, 'w', encoding='utf-8') as f:
                    f.write(result['markdown'])
                result['saved_file'] = doc_filename
            except Exception as e:
                result['file_save_error'] = str(e)
        
        return result
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/api/figma/variables/analyze")
async def analyze_figma_variables():
    """Analyze Figma variables and provide insights using RAG."""
    class VariableAnalysisRequest(BaseModel):
        file_key: str
        focus_areas: Optional[List[str]] = ["primitives", "alias", "semantics"]
        generate_recommendations: bool = True
    
    try:
        request_data = await request.json()
        analysis_request = VariableAnalysisRequest(**request_data)
        
        if not FIGMA_AVAILABLE:
            return {"error": "Figma service not available", "status": "error"}
        
        from figma import figma_service
        
        # Get variables data
        variables_result = figma_service.get_file_variables(analysis_request.file_key)
        if not variables_result['success']:
            return variables_result
        
        # Generate documentation
        doc_result = figma_service.generate_variables_documentation(
            analysis_request.file_key, 
            'markdown'
        )
        
        analysis = {
            'file_key': analysis_request.file_key,
            'timestamp': datetime.now().isoformat(),
            'collections_summary': {},
            'insights': [],
            'recommendations': []
        }
        
        # Analyze collections
        for category, collections in doc_result['documentation'].items():
            if category in analysis_request.focus_areas:
                analysis['collections_summary'][category] = {
                    'count': len(collections),
                    'total_variables': sum(len(c['variables']) for c in collections),
                    'collections': [{'name': c['name'], 'variable_count': len(c['variables'])} for c in collections]
                }
        
        # Generate insights using RAG if available
        if RAG_AVAILABLE and analysis_request.generate_recommendations:
            variables_context = f"Figma design system analysis: {json.dumps(analysis['collections_summary'])}"
            
            rag_insights = get_contextual_insights(
                "design system variables optimization recommendations", 
                context=variables_context
            )
            
            if rag_insights.get('success'):
                analysis['rag_insights'] = rag_insights.get('insights', {})
        
        return {
            'success': True,
            'analysis': analysis,
            'documentation': doc_result if doc_result['success'] else None,
            'raw_variables': variables_result
        }
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

# For local development and Cloud Run
if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for Cloud Run, default to 8000 for local
    port = int(os.getenv("PORT", 8000))
    print("🚀 Starting Beth's Assistant Backend with RAG...")
    print("🧠 RAG Learning: ENABLED" if RAG_AVAILABLE else "🧠 RAG Learning: DISABLED")
    print(f"📍 Health check: http://localhost:{port}/health")
    print(f"📖 API docs: http://localhost:{port}/docs")
    print(f"🔍 RAG insights: http://localhost:{port}/api/rag/stats")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
