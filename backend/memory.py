"""
Memory service for Beth's unified assistant.
Handles conversation memory, learning, and context management using SQLite.
"""

import os
import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import hashlib
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the memory database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        user_id TEXT,
                        title TEXT,
                        summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0,
                        importance_score INTEGER DEFAULT 1
                    )
                ''')
                
                # Messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        conversation_id TEXT,
                        role TEXT CHECK(role IN ('user', 'assistant', 'system')),
                        content TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                    )
                ''')
                
                # Memory entries table (for long-term memory)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id TEXT PRIMARY KEY,
                        type TEXT CHECK(type IN ('fact', 'preference', 'context', 'skill', 'relationship')),
                        category TEXT,
                        content TEXT,
                        importance INTEGER DEFAULT 1,
                        confidence REAL DEFAULT 1.0,
                        source_conversation_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TIMESTAMP,
                        tags TEXT,
                        FOREIGN KEY (source_conversation_id) REFERENCES conversations (id)
                    )
                ''')
                
                # Context embeddings table (for semantic search - simplified)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS context_embeddings (
                        id TEXT PRIMARY KEY,
                        content TEXT,
                        embedding_hash TEXT,
                        memory_entry_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (memory_entry_id) REFERENCES memory_entries (id)
                    )
                ''')
                
                # User preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id TEXT PRIMARY KEY,
                        category TEXT,
                        key TEXT,
                        value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(category, key)
                    )
                ''')
                
                conn.commit()
                logger.info("Memory database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def create_conversation(self, user_id: str = "beth", title: str = None) -> Dict:
        """Create a new conversation session."""
        try:
            conversation_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (id, user_id, title)
                    VALUES (?, ?, ?)
                ''', (conversation_id, user_id, title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
                conn.commit()
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'message': 'Conversation created successfully'
            }
            
        except Exception as e:
            logger.error(f"Create conversation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   metadata: Dict = None) -> Dict:
        """Add a message to a conversation."""
        try:
            message_id = str(uuid.uuid4())
            metadata_json = json.dumps(metadata) if metadata else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert message
                cursor.execute('''
                    INSERT INTO messages (id, conversation_id, role, content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (message_id, conversation_id, role, content, metadata_json))
                
                # Update conversation message count and timestamp
                cursor.execute('''
                    UPDATE conversations 
                    SET message_count = message_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (conversation_id,))
                
                conn.commit()
            
            return {
                'success': True,
                'message_id': message_id,
                'message': 'Message added successfully'
            }
            
        except Exception as e:
            logger.error(f"Add message error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> Dict:
        """Get message history for a conversation."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT role, content, timestamp, metadata
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (conversation_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    role, content, timestamp, metadata_json = row
                    metadata = json.loads(metadata_json) if metadata_json else {}
                    
                    messages.append({
                        'role': role,
                        'content': content,
                        'timestamp': timestamp,
                        'metadata': metadata
                    })
                
                # Reverse to get chronological order
                messages.reverse()
                
                return {
                    'success': True,
                    'messages': messages,
                    'count': len(messages)
                }
                
        except Exception as e:
            logger.error(f"Get conversation history error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def save_memory(self, memory_type: str, content: str, category: str = None,
                   importance: int = 1, confidence: float = 1.0,
                   source_conversation_id: str = None, tags: List[str] = None) -> Dict:
        """Save a memory entry for long-term storage."""
        try:
            memory_id = str(uuid.uuid4())
            tags_json = json.dumps(tags) if tags else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memory_entries 
                    (id, type, category, content, importance, confidence, 
                     source_conversation_id, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (memory_id, memory_type, category, content, importance, 
                      confidence, source_conversation_id, tags_json))
                conn.commit()
            
            return {
                'success': True,
                'memory_id': memory_id,
                'message': 'Memory saved successfully'
            }
            
        except Exception as e:
            logger.error(f"Save memory error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_memories(self, query: str, memory_type: str = None, 
                       category: str = None, limit: int = 10) -> Dict:
        """Search through saved memories."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic query
                sql = '''
                    SELECT id, type, category, content, importance, confidence,
                           created_at, access_count, tags
                    FROM memory_entries
                    WHERE content LIKE ?
                '''
                params = [f'%{query}%']
                
                if memory_type:
                    sql += ' AND type = ?'
                    params.append(memory_type)
                
                if category:
                    sql += ' AND category = ?'
                    params.append(category)
                
                sql += ' ORDER BY importance DESC, confidence DESC, access_count DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(sql, params)
                
                memories = []
                for row in cursor.fetchall():
                    memory_id, mem_type, cat, content, importance, confidence, created_at, access_count, tags_json = row
                    tags = json.loads(tags_json) if tags_json else []
                    
                    memories.append({
                        'id': memory_id,
                        'type': mem_type,
                        'category': cat,
                        'content': content,
                        'importance': importance,
                        'confidence': confidence,
                        'created_at': created_at,
                        'access_count': access_count,
                        'tags': tags
                    })
                
                # Update access count for found memories
                if memories:
                    memory_ids = [m['id'] for m in memories]
                    placeholders = ','.join(['?'] * len(memory_ids))
                    cursor.execute(f'''
                        UPDATE memory_entries 
                        SET access_count = access_count + 1,
                            last_accessed = CURRENT_TIMESTAMP
                        WHERE id IN ({placeholders})
                    ''', memory_ids)
                    conn.commit()
                
                return {
                    'success': True,
                    'memories': memories,
                    'count': len(memories),
                    'query': query
                }
                
        except Exception as e:
            logger.error(f"Search memories error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_conversations(self, days: int = 7, limit: int = 10) -> Dict:
        """Get recent conversations."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, summary, created_at, updated_at, 
                           message_count, importance_score
                    FROM conversations
                    WHERE updated_at >= ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                ''', (cutoff_date, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conv_id, title, summary, created_at, updated_at, msg_count, importance = row
                    conversations.append({
                        'id': conv_id,
                        'title': title,
                        'summary': summary,
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'message_count': msg_count,
                        'importance_score': importance
                    })
                
                return {
                    'success': True,
                    'conversations': conversations,
                    'count': len(conversations),
                    'days': days
                }
                
        except Exception as e:
            logger.error(f"Get recent conversations error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_conversation_summary(self, conversation_id: str, summary: str, 
                                  importance_score: int = None) -> Dict:
        """Update conversation summary and importance."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if importance_score is not None:
                    cursor.execute('''
                        UPDATE conversations 
                        SET summary = ?, importance_score = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (summary, importance_score, conversation_id))
                else:
                    cursor.execute('''
                        UPDATE conversations 
                        SET summary = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (summary, conversation_id))
                
                conn.commit()
            
            return {
                'success': True,
                'message': 'Conversation summary updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Update conversation summary error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def save_user_preference(self, category: str, key: str, value: str) -> Dict:
        """Save or update a user preference."""
        try:
            pref_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (id, category, key, value, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (pref_id, category, key, value))
                conn.commit()
            
            return {
                'success': True,
                'message': f'Preference {category}.{key} saved successfully'
            }
            
        except Exception as e:
            logger.error(f"Save user preference error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_user_preferences(self, category: str = None) -> Dict:
        """Get user preferences, optionally filtered by category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('''
                        SELECT category, key, value, updated_at
                        FROM user_preferences
                        WHERE category = ?
                        ORDER BY category, key
                    ''', (category,))
                else:
                    cursor.execute('''
                        SELECT category, key, value, updated_at
                        FROM user_preferences
                        ORDER BY category, key
                    ''')
                
                preferences = {}
                for row in cursor.fetchall():
                    cat, key, value, updated_at = row
                    if cat not in preferences:
                        preferences[cat] = {}
                    preferences[cat][key] = {
                        'value': value,
                        'updated_at': updated_at
                    }
                
                return {
                    'success': True,
                    'preferences': preferences,
                    'category_filter': category
                }
                
        except Exception as e:
            logger.error(f"Get user preferences error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about the memory database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count conversations
                cursor.execute('SELECT COUNT(*) FROM conversations')
                conversation_count = cursor.fetchone()[0]
                
                # Count messages
                cursor.execute('SELECT COUNT(*) FROM messages')
                message_count = cursor.fetchone()[0]
                
                # Count memory entries by type
                cursor.execute('''
                    SELECT type, COUNT(*) 
                    FROM memory_entries 
                    GROUP BY type
                ''')
                memory_by_type = dict(cursor.fetchall())
                
                # Count preferences
                cursor.execute('SELECT COUNT(*) FROM user_preferences')
                preference_count = cursor.fetchone()[0]
                
                # Get most recent activity
                cursor.execute('''
                    SELECT MAX(updated_at) FROM conversations
                ''')
                last_conversation = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'stats': {
                        'conversations': conversation_count,
                        'messages': message_count,
                        'memory_entries': memory_by_type,
                        'preferences': preference_count,
                        'last_conversation': last_conversation,
                        'database_path': self.db_path
                    }
                }
                
        except Exception as e:
            logger.error(f"Get memory stats error: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global instance
memory_service = MemoryService()

# Convenience functions for main.py
def create_conversation_session(user_id: str = "beth", title: str = None) -> Dict:
    return memory_service.create_conversation(user_id, title)

def add_conversation_message(conversation_id: str, role: str, content: str, 
                           metadata: Dict = None) -> Dict:
    return memory_service.add_message(conversation_id, role, content, metadata)

def get_conversation_messages(conversation_id: str, limit: int = 50) -> Dict:
    return memory_service.get_conversation_history(conversation_id, limit)

def save_long_term_memory(memory_type: str, content: str, category: str = None,
                         importance: int = 1, conversation_id: str = None) -> Dict:
    return memory_service.save_memory(memory_type, content, category, importance, 
                                     source_conversation_id=conversation_id)

def search_memory_bank(query: str, memory_type: str = None, limit: int = 10) -> Dict:
    return memory_service.search_memories(query, memory_type, limit=limit)

def get_memory_statistics() -> Dict:
    return memory_service.get_memory_stats()
