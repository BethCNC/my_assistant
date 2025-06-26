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

# Firebase Functions import
from firebase_functions import https_fn
from firebase_admin import initialize_app
import firebase_admin

# Initialize Firebase Admin
try:
    initialize_app()
except ValueError:
    # App already initialized, continue
    pass

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Beth Assistant API", version="1.0.0")

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
    return {"message": "Beth Assistant API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Basic chat endpoint
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatMessage):
    """Basic chat endpoint."""
    try:
        # For now, return a simple response
        # TODO: Integrate with OpenAI and other services
        return {
            "response": f"I received your message: {chat_request.message}",
            "conversation_id": chat_request.conversation_id or "new-conversation",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/chats")
async def get_conversations():
    """Get list of conversations."""
    try:
        # Mock conversation data for now
        # TODO: Integrate with database
        mock_conversations = [
            {
                "id": "1",
                "title": "How can I better update my design tokens",
                "preview": "Discussion about design system tokens",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "2", 
                "title": "How can I better organize my projects",
                "preview": "Project organization strategies",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "3",
                "title": "How can I better manage my calendar",
                "preview": "Calendar management tips",
                "timestamp": datetime.now().isoformat()
            }
        ]
        return mock_conversations
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/chats/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get chat history for a specific conversation."""
    try:
        # Mock chat history for now
        # TODO: Integrate with database
        mock_messages = [
            {
                "id": "1",
                "content": "How can I better update my design tokens?",
                "role": "user",
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conversation_id
            },
            {
                "id": "2",
                "content": "I can help you with design tokens! Here are some best practices...",
                "role": "assistant", 
                "timestamp": datetime.now().isoformat(),
                "conversation_id": conversation_id
            }
        ]
        return mock_messages
    except Exception as e:
        return {"error": str(e), "status": "error"}

# Firebase Functions export
@https_fn.on_request()
def api(req):
    """Firebase Functions entry point."""
    return app(req.environ, req.start_response)

# For local development
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Beth's Assistant Backend...")
    print("📍 Health check: http://localhost:8000/health")
    print("📖 API docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
