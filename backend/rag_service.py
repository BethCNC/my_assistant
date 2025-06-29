"""
RAG (Retrieval-Augmented Generation) service for Beth's unified assistant.
Learns user habits, preferences, and system usage patterns to improve responses.
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from sentence_transformers import SentenceTransformer
import chromadb
import sqlite3
import openai
from dataclasses import dataclass
import hashlib
import uuid
import signal
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def timeout(duration):
    """Context manager for timeout operations."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {duration} seconds")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    try:
        yield
    finally:
        signal.alarm(0)

@dataclass
class RAGDocument:
    """Represents a document in the RAG system."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    source: str = "unknown"
    importance: float = 1.0

class RAGService:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self.embedding_model = None
        self.chroma_client = None
        self.collections = {}
        
        # Temporarily disable ChromaDB to avoid hanging
        logger.info("Initializing RAG service in fallback mode (ChromaDB disabled)")
        self._init_fallback_mode()
        
        # TODO: Re-enable ChromaDB initialization once stability issues are resolved
        # try:
        #     with timeout(30):  # 30 second timeout
        #         logger.info("Initializing RAG service components...")
        #         
        #         # Initialize embedding model
        #         logger.info("Loading sentence transformer...")
        #         self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        #         
        #         # Initialize ChromaDB with simpler settings
        #         logger.info("Initializing ChromaDB...")
        #         self.chroma_client = chromadb.PersistentClient(
        #             path="./chroma_db",
        #             settings=chromadb.Settings(
        #                 anonymized_telemetry=False,
        #                 allow_reset=True
        #             )
        #         )
        #         
        #         # Create collections for different types of knowledge
        #         logger.info("Setting up collections...")
        #         self.collections = {
        #             'conversations': self._get_or_create_collection('conversations'),
        #             'habits': self._get_or_create_collection('user_habits'),
        #             'preferences': self._get_or_create_collection('user_preferences'),
        #             'system_usage': self._get_or_create_collection('system_usage'),
        #             'knowledge_base': self._get_or_create_collection('knowledge_base'),
        #             'workflows': self._get_or_create_collection('workflows')
        #         }
        #         
        # except TimeoutError:
        #     logger.error("RAG service initialization timed out - running in degraded mode")
        #     self._init_fallback_mode()
        # except Exception as e:
        #     logger.error(f"RAG service initialization failed: {str(e)} - running in degraded mode")
        #     self._init_fallback_mode()
        
        # OpenAI client for enhanced generation
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize habit tracking
        self.habit_patterns = {}
        self.usage_analytics = {}
        
        logger.info("RAG service initialized successfully")
    
    def _init_fallback_mode(self):
        """Initialize RAG service in fallback mode without vector storage."""
        logger.warning("Running RAG service in fallback mode (no vector storage)")
        self.embedding_model = None
        self.chroma_client = None
        self.collections = {}
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        if not self.chroma_client:
            return None
            
        try:
            return self.chroma_client.get_collection(name)
        except:
            return self.chroma_client.create_collection(name)
    
    def is_enabled(self) -> bool:
        """Check if RAG service is fully enabled."""
        return self.chroma_client is not None and self.embedding_model is not None
    
    def learn_from_conversation(self, conversation_id: str, messages: List[Dict], 
                              context: Dict = None) -> Dict:
        """Learn from a conversation to improve future responses."""
        try:
            # Extract learning points from conversation
            learning_points = self._extract_learning_points(messages, context)
            
            # Only store embeddings if RAG is fully enabled
            if self.is_enabled():
                # Store conversation embedding
                conversation_text = self._format_conversation_for_embedding(messages)
                embedding = self.embedding_model.encode(conversation_text).tolist()
                
                # Store in ChromaDB
                self.collections['conversations'].add(
                    embeddings=[embedding],
                    documents=[conversation_text],
                    metadatas=[{
                        'conversation_id': conversation_id,
                        'timestamp': datetime.now().isoformat(),
                        'message_count': len(messages),
                        'topics': learning_points.get('topics', []),
                        'user_intent': learning_points.get('intent', 'unknown'),
                        'satisfaction_score': learning_points.get('satisfaction', 0.5)
                    }],
                    ids=[f"conv_{conversation_id}"]
                )
            
            # Update habit patterns (works in fallback mode too)
            self._update_habit_patterns(learning_points)
            
            # Update usage analytics (works in fallback mode too)
            self._update_usage_analytics(conversation_id, messages, context)
            
            return {
                'success': True,
                'learning_points': len(learning_points.get('insights', [])),
                'message': 'Conversation learning completed',
                'rag_enabled': self.is_enabled()
            }
            
        except Exception as e:
            logger.error(f"Learn from conversation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_learning_points(self, messages: List[Dict], context: Dict = None) -> Dict:
        """Extract learning points from conversation messages."""
        learning_points = {
            'topics': [],
            'intent': 'unknown',
            'satisfaction': 0.5,
            'insights': [],
            'user_patterns': []
        }
        
        try:
            # Analyze conversation with OpenAI
            conversation_text = self._format_conversation_for_analysis(messages)
            
            prompt = f"""
            Analyze this conversation and extract learning points for improving an AI assistant:
            
            Conversation:
            {conversation_text}
            
            Please identify:
            1. Main topics discussed
            2. User's intent and goals
            3. User satisfaction indicators (1-10 scale)
            4. Key insights about user preferences
            5. Patterns in how the user interacts
            6. Areas where the assistant could improve
            
            Return as JSON with keys: topics, intent, satisfaction, insights, user_patterns, improvement_areas
            """
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            learning_points.update(analysis)
            
        except Exception as e:
            logger.warning(f"OpenAI analysis failed, using fallback: {str(e)}")
            # Fallback to simple keyword extraction
            learning_points = self._fallback_learning_extraction(messages)
        
        return learning_points
    
    def _fallback_learning_extraction(self, messages: List[Dict]) -> Dict:
        """Fallback method for extracting learning points without OpenAI."""
        topics = set()
        patterns = []
        
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()
                
                # Simple topic extraction
                if 'figma' in content or 'design' in content:
                    topics.add('design')
                if 'notion' in content or 'task' in content:
                    topics.add('productivity')
                if 'github' in content or 'code' in content:
                    topics.add('development')
                if 'calendar' in content or 'schedule' in content:
                    topics.add('scheduling')
                
                # Pattern detection
                if content.startswith('how can i'):
                    patterns.append('help_seeking')
                if '?' in content:
                    patterns.append('question_asking')
        
        return {
            'topics': list(topics),
            'intent': 'help_seeking' if 'help_seeking' in patterns else 'unknown',
            'satisfaction': 0.7,  # Default neutral-positive
            'insights': [],
            'user_patterns': patterns
        }
    
    def _update_habit_patterns(self, learning_points: Dict):
        """Update user habit patterns based on learning points."""
        timestamp = datetime.now().isoformat()
        
        # Track topic preferences
        for topic in learning_points.get('topics', []):
            if topic not in self.habit_patterns:
                self.habit_patterns[topic] = {
                    'frequency': 0,
                    'last_accessed': timestamp,
                    'preference_score': 0.5
                }
            
            self.habit_patterns[topic]['frequency'] += 1
            self.habit_patterns[topic]['last_accessed'] = timestamp
            
            # Adjust preference score based on satisfaction
            satisfaction = learning_points.get('satisfaction', 0.5)
            current_score = self.habit_patterns[topic]['preference_score']
            # Weighted average with new satisfaction score
            self.habit_patterns[topic]['preference_score'] = (current_score * 0.8) + (satisfaction * 0.2)
        
        # Store habits in vector database
        self._store_habits_in_vector_db()
    
    def _store_habits_in_vector_db(self):
        """Store habit patterns in vector database for retrieval."""
        try:
            # Only store embeddings if RAG is fully enabled
            if self.is_enabled():
                for topic, pattern in self.habit_patterns.items():
                    habit_text = f"User frequently discusses {topic}. Preference score: {pattern['preference_score']:.2f}. Last accessed: {pattern['last_accessed']}"
                    embedding = self.embedding_model.encode(habit_text).tolist()
                    
                    self.collections['habits'].upsert(
                        embeddings=[embedding],
                        documents=[habit_text],
                        metadatas=[{
                            'topic': topic,
                            'frequency': pattern['frequency'],
                            'preference_score': pattern['preference_score'],
                            'last_accessed': pattern['last_accessed']
                        }],
                        ids=[f"habit_{topic}"]
                    )
        except Exception as e:
            logger.error(f"Store habits error: {str(e)}")
    
    def _update_usage_analytics(self, conversation_id: str, messages: List[Dict], context: Dict):
        """Update system usage analytics."""
        usage_data = {
            'timestamp': datetime.now().isoformat(),
            'conversation_id': conversation_id,
            'message_count': len(messages),
            'user_messages': len([m for m in messages if m.get('role') == 'user']),
            'assistant_messages': len([m for m in messages if m.get('role') == 'assistant']),
            'context': context or {}
        }
        
        # Only store embeddings if RAG is fully enabled
        if self.is_enabled():
            # Store usage pattern
            usage_text = f"System usage: {usage_data['message_count']} messages, {usage_data['user_messages']} user messages"
            embedding = self.embedding_model.encode(usage_text).tolist()
            
            self.collections['system_usage'].add(
                embeddings=[embedding],
                documents=[usage_text],
                metadatas=[usage_data],
                ids=[f"usage_{conversation_id}_{datetime.now().timestamp()}"]
            )
        
        # Store analytics in memory for fallback mode
        self.usage_analytics[conversation_id] = usage_data
    
    def get_contextual_insights(self, query: str, limit: int = 5) -> Dict:
        """Get contextual insights based on user query and learned patterns."""
        try:
            insights = {}
            
            # Only do vector search if RAG is fully enabled
            if self.is_enabled():
                # Generate query embedding
                query_embedding = self.embedding_model.encode(query).tolist()
                
                # Search across all collections
                for collection_name, collection in self.collections.items():
                    try:
                        results = collection.query(
                            query_embeddings=[query_embedding],
                            n_results=min(limit, 10)
                        )
                        
                        if results['documents'] and results['documents'][0]:
                            insights[collection_name] = {
                                'documents': results['documents'][0],
                                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                                'distances': results['distances'][0] if results['distances'] else []
                            }
                    except Exception as e:
                        logger.warning(f"Query {collection_name} failed: {str(e)}")
                        continue
            else:
                # Fallback mode - use simple pattern matching
                insights = self._get_fallback_insights(query)
            
            return {
                'success': True,
                'insights': insights,
                'query': query,
                'rag_enabled': self.is_enabled()
            }
            
        except Exception as e:
            logger.error(f"Get contextual insights error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_fallback_insights(self, query: str) -> Dict:
        """Get insights in fallback mode using simple pattern matching."""
        insights = {}
        query_lower = query.lower()
        
        # Simple keyword-based insights
        if any(word in query_lower for word in ['figma', 'design', 'ui', 'component']):
            insights['design_patterns'] = {
                'documents': ['User frequently works with Figma design systems'],
                'metadatas': [{'type': 'design_preference', 'confidence': 0.7}],
                'distances': [0.3]
            }
        
        if any(word in query_lower for word in ['notion', 'task', 'productivity', 'organize']):
            insights['productivity_patterns'] = {
                'documents': ['User prefers organized, systematic approaches'],
                'metadatas': [{'type': 'productivity_preference', 'confidence': 0.7}],
                'distances': [0.3]
            }
        
        return insights
    
    def generate_enhanced_response(self, query: str, context: Dict = None) -> Dict:
        """Generate enhanced response using RAG."""
        try:
            # Get contextual insights
            insights = self.get_contextual_insights(query)
            
            # Build enhanced context
            enhanced_context = self._build_enhanced_context(query, insights, context)
            
            # Generate response with OpenAI
            response = self._generate_with_openai(query, enhanced_context)
            
            return {
                'success': True,
                'response': response,
                'context_used': len(enhanced_context.get('relevant_docs', [])),
                'insights_applied': list(insights.get('insights', {}).keys())
            }
            
        except Exception as e:
            logger.error(f"Generate enhanced response error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _build_enhanced_context(self, query: str, insights: Dict, context: Dict = None) -> Dict:
        """Build enhanced context from RAG insights."""
        enhanced_context = {
            'original_query': query,
            'relevant_docs': [],
            'user_habits': [],
            'system_patterns': [],
            'preferences': []
        }
        
        # Extract relevant information from insights
        for collection_name, collection_data in insights.get('insights', {}).items():
            docs = collection_data.get('documents', [])
            metadatas = collection_data.get('metadatas', [])
            
            for i, doc in enumerate(docs[:3]):  # Top 3 most relevant
                metadata = metadatas[i] if i < len(metadatas) else {}
                
                if collection_name == 'habits':
                    enhanced_context['user_habits'].append({
                        'content': doc,
                        'metadata': metadata
                    })
                elif collection_name == 'preferences':
                    enhanced_context['preferences'].append({
                        'content': doc,
                        'metadata': metadata
                    })
                elif collection_name == 'system_usage':
                    enhanced_context['system_patterns'].append({
                        'content': doc,
                        'metadata': metadata
                    })
                else:
                    enhanced_context['relevant_docs'].append({
                        'content': doc,
                        'metadata': metadata,
                        'source': collection_name
                    })
        
        return enhanced_context
    
    def _generate_with_openai(self, query: str, enhanced_context: Dict) -> str:
        """Generate response using OpenAI with enhanced context."""
        try:
            # Build context-aware prompt
            context_prompt = self._build_context_prompt(query, enhanced_context)
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Beth's personal AI assistant. Use the provided context about her habits, preferences, and past interactions to give personalized, helpful responses."},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            return f"I understand you're asking about: {query}. Let me help you with that based on what I know about your preferences."
    
    def _build_context_prompt(self, query: str, enhanced_context: Dict) -> str:
        """Build context-aware prompt for OpenAI."""
        prompt_parts = [f"User Query: {query}\n"]
        
        # Add user habits
        if enhanced_context['user_habits']:
            prompt_parts.append("User Habits & Patterns:")
            for habit in enhanced_context['user_habits'][:2]:
                prompt_parts.append(f"- {habit['content']}")
            prompt_parts.append("")
        
        # Add preferences
        if enhanced_context['preferences']:
            prompt_parts.append("User Preferences:")
            for pref in enhanced_context['preferences'][:2]:
                prompt_parts.append(f"- {pref['content']}")
            prompt_parts.append("")
        
        # Add relevant documents
        if enhanced_context['relevant_docs']:
            prompt_parts.append("Relevant Context:")
            for doc in enhanced_context['relevant_docs'][:3]:
                prompt_parts.append(f"- {doc['content'][:200]}...")
            prompt_parts.append("")
        
        prompt_parts.append("Please provide a personalized response based on this context.")
        
        return "\n".join(prompt_parts)
    
    def _format_conversation_for_embedding(self, messages: List[Dict]) -> str:
        """Format conversation for embedding storage."""
        formatted_messages = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted_messages.append(f"{role}: {content}")
        return "\n".join(formatted_messages)
    
    def _format_conversation_for_analysis(self, messages: List[Dict]) -> str:
        """Format conversation for OpenAI analysis."""
        return self._format_conversation_for_embedding(messages)
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about what the system has learned."""
        try:
            stats = {
                'total_conversations': 0,
                'total_habits': len(self.habit_patterns),
                'top_topics': [],
                'learning_quality': 0.0
            }
            
            # Get collection counts
            for name, collection in self.collections.items():
                count = collection.count()
                stats[f'{name}_count'] = count
                if name == 'conversations':
                    stats['total_conversations'] = count
            
            # Get top topics from habits
            sorted_habits = sorted(
                self.habit_patterns.items(),
                key=lambda x: x[1]['frequency'],
                reverse=True
            )
            stats['top_topics'] = [
                {'topic': topic, 'frequency': data['frequency'], 'preference': data['preference_score']}
                for topic, data in sorted_habits[:5]
            ]
            
            # Calculate learning quality (average preference score)
            if self.habit_patterns:
                total_preference = sum(data['preference_score'] for data in self.habit_patterns.values())
                stats['learning_quality'] = total_preference / len(self.habit_patterns)
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Get learning stats error: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global instance
rag_service = RAGService()

# Convenience functions for main.py
def learn_from_conversation(conversation_id: str, messages: List[Dict], context: Dict = None) -> Dict:
    return rag_service.learn_from_conversation(conversation_id, messages, context)

def get_enhanced_response(query: str, context: Dict = None) -> Dict:
    return rag_service.generate_enhanced_response(query, context)

def get_contextual_insights(query: str, limit: int = 5) -> Dict:
    return rag_service.get_contextual_insights(query, limit)

def get_rag_learning_stats() -> Dict:
    return rag_service.get_learning_stats() 