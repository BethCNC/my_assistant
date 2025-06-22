from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from notion_client import Client
import requests
import openai
import sqlite3
import traceback
import json
from datetime import datetime
from typing import List, Optional

# Import our service modules
from notion import NotionService
from figma import FigmaService
from github import GitHubService
from memory import MemoryService, create_conversation_session, add_conversation_message

load_dotenv()

# Initialize services
try:
    notion_service = NotionService()
    print("✅ Notion service initialized")
except Exception as e:
    print(f"⚠️ Notion service failed to initialize: {e}")
    notion_service = None

try:
    figma_service = FigmaService()
    print("✅ Figma service initialized")
except Exception as e:
    print(f"⚠️ Figma service failed to initialize: {e}")
    figma_service = None

try:
    github_service = GitHubService()
    print("✅ GitHub service initialized")
except Exception as e:
    print(f"⚠️ GitHub service failed to initialize: {e}")
    github_service = None

try:
    memory_service = MemoryService()
    print("✅ Memory service initialized")
except Exception as e:
    print(f"⚠️ Memory service failed to initialize: {e}")
    memory_service = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint to verify all services are running."""
    services_status = {
        "notion": notion_service is not None,
        "figma": figma_service is not None,
        "github": github_service is not None,
        "memory": memory_service is not None,
        "openai": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    all_healthy = all(services_status.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    }

# Individual service health checks
@app.get("/api/notion/health")
async def notion_health():
    """Check if Notion service is connected and working."""
    if notion_service is None:
        return {"status": "disconnected", "error": "Service not initialized"}
    
    try:
        # Try a simple operation to verify connection
        await notion_service.test_connection()
        return {"status": "connected", "service": "notion"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@app.get("/api/figma/health")
async def figma_health():
    """Check if Figma service is connected and working."""
    if figma_service is None:
        return {"status": "disconnected", "error": "Service not initialized"}
    
    try:
        # Try a simple operation to verify connection
        await figma_service.test_connection()
        return {"status": "connected", "service": "figma"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@app.get("/api/github/health")
async def github_health():
    """Check if GitHub service is connected and working."""
    if github_service is None:
        return {"status": "disconnected", "error": "Service not initialized"}
    
    try:
        # Try a simple operation to verify connection
        await github_service.test_connection()
        return {"status": "connected", "service": "github"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

@app.get("/api/email/health")
async def email_health():
    """Check if Email service is connected and working."""
    # For now, return disconnected as we haven't implemented email service yet
    return {"status": "disconnected", "error": "Email service not implemented"}

@app.get("/api/calendar/health")
async def calendar_health():
    """Check if Calendar service is connected and working."""
    # For now, return disconnected as we haven't implemented calendar service yet
    return {"status": "disconnected", "error": "Calendar service not implemented"}

class SaveChatRequest(BaseModel):
    chat_id: str
    title: str
    messages: List[dict]

# Database initialization
def init_database():
    """Initialize the SQLite database with chat history tables."""
    db_path = "../agent_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create chats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            preview TEXT,
            message_count INTEGER DEFAULT 0
        )
    """)
    
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            type TEXT NOT NULL,  -- 'user', 'assistant', 'system'
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sender_name TEXT,
            metadata TEXT,  -- JSON for additional data
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages (chat_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats (updated_at)")
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

def get_db_connection():
    """Get a database connection."""
    db_path = "../agent_memory.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn

def save_chat(chat_id: str, title: str, messages: List[dict]) -> dict:
    """Save a complete chat conversation to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert or update chat
        preview = messages[0]['message'][:100] + '...' if messages and len(messages[0]['message']) > 100 else messages[0]['message'] if messages else ''
        
        cursor.execute("""
            INSERT OR REPLACE INTO chats (id, title, updated_at, preview, message_count)
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, title, datetime.now(), preview, len(messages)))
        
        # Delete existing messages for this chat
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        
        # Insert all messages
        for msg in messages:
            cursor.execute("""
                INSERT INTO messages (id, chat_id, type, message, timestamp, sender_name, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                msg.get('id', f"msg_{datetime.now().timestamp()}"),
                chat_id,
                msg.get('type', 'user'),
                msg.get('message', ''),
                msg.get('timestamp', datetime.now()),
                msg.get('senderName', ''),
                json.dumps(msg.get('metadata', {}))
            ))
        
        conn.commit()
        conn.close()
        return {"success": True, "message": "Chat saved successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def load_chat(chat_id: str) -> dict:
    """Load a specific chat conversation from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get chat info
        cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
        chat_row = cursor.fetchone()
        
        if not chat_row:
            return {"success": False, "error": "Chat not found"}
        
        # Get messages
        cursor.execute("""
            SELECT * FROM messages 
            WHERE chat_id = ? 
            ORDER BY timestamp ASC
        """, (chat_id,))
        
        message_rows = cursor.fetchall()
        
        messages = []
        for row in message_rows:
            msg = {
                "id": row["id"],
                "type": row["type"],
                "message": row["message"],
                "timestamp": row["timestamp"],
                "senderName": row["sender_name"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            }
            messages.append(msg)
        
        chat_data = {
            "id": chat_row["id"],
            "title": chat_row["title"],
            "created_at": chat_row["created_at"],
            "updated_at": chat_row["updated_at"],
            "preview": chat_row["preview"],
            "message_count": chat_row["message_count"],
            "messages": messages
        }
        
        conn.close()
        return {"success": True, "chat": chat_data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_all_chats() -> dict:
    """Get all chat conversations (metadata only, not full messages)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, created_at, updated_at, preview, message_count
            FROM chats 
            ORDER BY updated_at DESC
        """)
        
        chat_rows = cursor.fetchall()
        
        chats = []
        for row in chat_rows:
            chat = {
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "preview": row["preview"],
                "message_count": row["message_count"]
            }
            chats.append(chat)
        
        conn.close()
        return {"success": True, "chats": chats}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def add_message_to_chat(chat_id: str, message_type: str, message: str, sender_name: str = "") -> dict:
    """Add a single message to an existing chat."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        message_id = f"msg_{datetime.now().timestamp()}"
        
        # Insert message
        cursor.execute("""
            INSERT INTO messages (id, chat_id, type, message, timestamp, sender_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, chat_id, message_type, message, datetime.now(), sender_name))
        
        # Update chat's updated_at and message_count
        cursor.execute("""
            UPDATE chats 
            SET updated_at = ?, 
                message_count = (SELECT COUNT(*) FROM messages WHERE chat_id = ?),
                preview = CASE WHEN ? = 'user' THEN ? ELSE preview END
            WHERE id = ?
        """, (datetime.now(), chat_id, message_type, message[:100], chat_id))
        
        conn.commit()
        conn.close()
        return {"success": True, "message_id": message_id}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Simple in-memory chat history for RAG (kept for backward compatibility)
chat_history = []

# Updated log_interaction function to use SQLite
def log_interaction(user, intent, message, result):
    """Log interaction for analytics (can be expanded)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create interactions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                intent TEXT,
                message TEXT,
                result TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO interactions (user, intent, message, result)
            VALUES (?, ?, ?, ?)
        """, (user, intent, message, result))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

# API Endpoints for Chat History
@app.post("/api/chats/save")
async def save_chat_endpoint(req: SaveChatRequest):
    """Save a complete chat conversation."""
    result = save_chat(req.chat_id, req.title, req.messages)
    return result

@app.get("/api/chats/{chat_id}")
async def load_chat_endpoint(chat_id: str):
    """Load a specific chat conversation."""
    result = load_chat(chat_id)
    return result

@app.get("/api/chats")
async def get_chats_endpoint():
    """Get all chat conversations (metadata only)."""
    result = get_all_chats()
    return result

@app.post("/api/chats/{chat_id}/messages")
async def add_message_endpoint(chat_id: str, req: ChatRequest):
    """Add a message to an existing chat."""
    result = add_message_to_chat(chat_id, "user", req.message, "Beth")
    return result

@app.delete("/api/chats/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    """Delete a chat conversation."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete messages first (due to foreign key constraint)
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        
        # Delete chat
        cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Chat deleted successfully"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    user_msg = req.message
    chat_history.append({"role": "user", "content": user_msg})
    context = chat_history[-10:]
    system_prompt = (
        "You are Beth's unified digital assistant. "
        "You have access to Notion, Figma, and GitHub. "
        "Given the user's message and recent chat history, decide which tool to use and answer naturally. "
        "If the user asks about tasks, projects, or notes, use Notion. "
        "If they ask about design files, use Figma. "
        "If they ask about code or repos, use GitHub. "
        "If you need to, ask clarifying questions. "
        "Respond with a JSON object: {{'intent': 'notion'|'figma'|'github'|'memory'|'clarify', 'answer': '...'}}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        *context,
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300
    )
    ai_raw = response.choices[0].message.content
    import json as pyjson
    try:
        ai_json = pyjson.loads(ai_raw.replace("'", '"'))
        intent = ai_json.get('intent', 'clarify')
        answer = ai_json.get('answer', ai_raw)
    except Exception:
        intent = 'clarify'
        answer = ai_raw
    # Route to real API if intent is actionable
    result = None
    try:
        if intent == 'notion':
            token = os.getenv("NOTION_TOKEN")
            notion = Client(auth=token)
            results = notion.search(filter={"property": "object", "value": "database"})
            dbs = [
                {"id": db["id"], "title": db["title"][0]["plain_text"] if db["title"] else "Untitled"}
                for db in results.get("results", [])
            ]
            result = f"Notion databases:\n" + "\n".join([f"• {d['title']} ({d['id']})" for d in dbs])
        elif intent == 'figma':
            token = os.getenv("FIGMA_ACCESS_TOKEN")
            headers = {"X-Figma-Token": token}
            resp = requests.get("https://api.figma.com/v1/me/files", headers=headers)
            if resp.status_code != 200:
                result = f"Figma API error: {resp.status_code}\n{resp.text}"
            else:
                files = resp.json().get("files", [])
                result = f"Figma files:\n" + "\n".join([f"• {f['name']} ({f['key']})" for f in files])
        elif intent == 'github':
            token = os.getenv("GITHUB_TOKEN")
            headers = {"Authorization": f"token {token}"}
            resp = requests.get("https://api.github.com/user/repos", headers=headers)
            if resp.status_code != 200:
                result = f"GitHub API error: {resp.status_code}\n{resp.text}"
            else:
                repos = resp.json()
                result = f"GitHub repos:\n" + "\n".join([f"• {r['name']}: {r['html_url']}" for r in repos])
        elif intent == 'memory':
            result = "Here's what I remember: " + " | ".join([m['content'] for m in chat_history[-5:]])
        else:
            result = answer
    except Exception as e:
        result = f"Error: {str(e)}\n{traceback.format_exc()}"
    chat_history.append({"role": "assistant", "content": result})
    log_interaction('user', intent, user_msg, result)
    return {"reply": result}

@app.get("/api/notion/databases")
async def get_notion_databases():
    """Get all accessible Notion databases."""
    if not notion_service:
        return {"error": "Notion service not available"}
    
    try:
        result = notion_service.get_all_databases()
        return result
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/notion/tasks")
async def get_notion_tasks():
    """Get tasks from Notion."""
    if not notion_service:
        return {"error": "Notion service not available"}
    
    try:
        result = notion_service.get_tasks()
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/notion/tasks")
async def create_notion_task(task_data: dict):
    """Create a new task in Notion."""
    if not notion_service:
        return {"error": "Notion service not available"}
    
    try:
        result = notion_service.create_task(
            title=task_data.get("title"),
            description=task_data.get("description"),
            priority=task_data.get("priority", "Medium"),
            due_date=task_data.get("due_date")
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/figma/files")
async def get_figma_files():
    """Get Figma files using the Figma service."""
    if not figma_service:
        return {"error": "Figma service not available"}
    
    try:
        result = figma_service.get_user_files()
        return result
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/figma/file/{file_key}")
async def get_figma_file_details(file_key: str):
    """Get details of a specific Figma file."""
    if not figma_service:
        return {"error": "Figma service not available"}
    
    try:
        result = figma_service.get_file_details(file_key)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/github/repos")
async def get_github_repos():
    """Get GitHub repositories using the GitHub service."""
    if not github_service:
        return {"error": "GitHub service not available"}
    
    try:
        result = github_service.get_user_repositories()
        return result
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory database statistics."""
    if not memory_service:
        return {"error": "Memory service not available"}
    
    try:
        result = memory_service.get_memory_stats()
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/memory/conversation")
async def create_memory_conversation(conversation_data: dict):
    """Create a new conversation in memory."""
    if not memory_service:
        return {"error": "Memory service not available"}
    
    try:
        result = create_conversation_session(
            user_id=conversation_data.get("user_id", "beth"),
            title=conversation_data.get("title")
        )
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Beth's Unified Assistant Backend...")
    print("📍 Health check: http://localhost:8000/health")
    print("📖 API docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
