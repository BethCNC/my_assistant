"""
Notion API service for Beth's unified assistant.
Handles tasks, projects, notes, clients, and health calendar management.
"""

import os
from typing import List, Dict, Optional, Any
from notion_client import Client
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError("NOTION_TOKEN not found in environment variables")
        
        self.client = Client(auth=self.token)
        
        # Database IDs from environment
        self.databases = {
            'tasks': os.getenv("TASKS_DATABASE_ID"),
            'projects': os.getenv("PROJECTS_DATABASE_ID"),
            'notes': os.getenv("NOTES_DATABASE_ID"),
            'clients': os.getenv("CLIENTS_DATABASE_ID"),
            'health': os.getenv("HEALTH_CALENDAR_DATABASE_ID"),
            'brand_assets': os.getenv("BRAND_ASSETS_DATABASE_ID"),
            'chat_memory': os.getenv("CHAT_MEMORY_DATABASE_ID")
        }
    
    async def test_connection(self):
        """Test the Notion API connection."""
        try:
            # Try to list users - simple API call to test connection
            self.client.users.list()
            return True
        except Exception as e:
            logger.error(f"Notion connection test failed: {e}")
            raise e
    
    def search_all_content(self, query: str, limit: int = 20) -> Dict:
        """Search across all accessible Notion content."""
        try:
            results = self.client.search(
                query=query,
                page_size=limit
            )
            
            formatted_results = []
            for item in results.get('results', []):
                formatted_item = {
                    'id': item['id'],
                    'type': item['object'],
                    'title': self._extract_title(item),
                    'url': item.get('url', ''),
                    'last_edited': item.get('last_edited_time', '')
                }
                formatted_results.append(formatted_item)
            
            return {
                'success': True,
                'results': formatted_results,
                'count': len(formatted_results)
            }
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_all_databases(self) -> Dict:
        """Get all available databases."""
        try:
            results = self.client.search(
                filter={"property": "object", "value": "database"}
            )
            
            databases = []
            for db in results.get('results', []):
                db_info = {
                    'id': db['id'],
                    'title': self._extract_title(db),
                    'url': db.get('url', ''),
                    'created_time': db.get('created_time', ''),
                    'last_edited_time': db.get('last_edited_time', '')
                }
                databases.append(db_info)
            
            return {
                'success': True,
                'databases': databases,
                'count': len(databases)
            }
            
        except Exception as e:
            logger.error(f"Database fetch error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def query_database(self, database_id: str, filter_conditions: Optional[Dict] = None, 
                      sorts: Optional[List[Dict]] = None, limit: int = 100) -> Dict:
        """Query a specific database with optional filters and sorting."""
        try:
            query_params = {'page_size': limit}
            
            if filter_conditions:
                query_params['filter'] = filter_conditions
            
            if sorts:
                query_params['sorts'] = sorts
            
            results = self.client.databases.query(
                database_id=database_id,
                **query_params
            )
            
            formatted_results = []
            for page in results.get('results', []):
                formatted_page = self._format_database_page(page)
                formatted_results.append(formatted_page)
            
            return {
                'success': True,
                'results': formatted_results,
                'count': len(formatted_results),
                'has_more': results.get('has_more', False)
            }
            
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_task(self, title: str, description: str = "", project: str = "", 
                   priority: str = "Medium", due_date: Optional[str] = None) -> Dict:
        """Create a new task in the tasks database."""
        if not self.databases['tasks']:
            return {'success': False, 'error': 'Tasks database ID not configured'}
        
        try:
            properties = {
                "Name": {"title": [{"text": {"content": title}}]},
                "Status": {"select": {"name": "Not Started"}},
                "Priority": {"select": {"name": priority}}
            }
            
            if description:
                properties["Description"] = {
                    "rich_text": [{"text": {"content": description}}]
                }
            
            if project:
                properties["Project"] = {
                    "rich_text": [{"text": {"content": project}}]
                }
            
            if due_date:
                properties["Due Date"] = {"date": {"start": due_date}}
            
            result = self.client.pages.create(
                parent={"database_id": self.databases['tasks']},
                properties=properties
            )
            
            return {
                'success': True,
                'task_id': result['id'],
                'url': result.get('url', ''),
                'message': f'Task "{title}" created successfully'
            }
            
        except Exception as e:
            logger.error(f"Task creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_task_status(self, task_id: str, status: str) -> Dict:
        """Update the status of a task."""
        try:
            self.client.pages.update(
                page_id=task_id,
                properties={
                    "Status": {"select": {"name": status}}
                }
            )
            
            return {
                'success': True,
                'message': f'Task status updated to "{status}"'
            }
            
        except Exception as e:
            logger.error(f"Task update error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_note(self, title: str, content: str, tags: List[str] = None) -> Dict:
        """Create a new note in the notes database."""
        if not self.databases['notes']:
            return {'success': False, 'error': 'Notes database ID not configured'}
        
        try:
            properties = {
                "Name": {"title": [{"text": {"content": title}}]},
                "Content": {"rich_text": [{"text": {"content": content}}]},
                "Created": {"date": {"start": datetime.now().isoformat()}}
            }
            
            if tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag} for tag in tags]
                }
            
            result = self.client.pages.create(
                parent={"database_id": self.databases['notes']},
                properties=properties
            )
            
            return {
                'success': True,
                'note_id': result['id'],
                'url': result.get('url', ''),
                'message': f'Note "{title}" created successfully'
            }
            
        except Exception as e:
            logger.error(f"Note creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_tasks(self, days: int = 7, status_filter: str = None) -> Dict:
        """Get recent tasks, optionally filtered by status."""
        if not self.databases['tasks']:
            return {'success': False, 'error': 'Tasks database ID not configured'}
        
        try:
            # Build filter for recent tasks
            date_filter = {
                "property": "Created",
                "date": {
                    "after": (datetime.now() - timedelta(days=days)).isoformat()
                }
            }
            
            filter_conditions = date_filter
            if status_filter:
                filter_conditions = {
                    "and": [
                        date_filter,
                        {
                            "property": "Status",
                            "select": {"equals": status_filter}
                        }
                    ]
                }
            
            return self.query_database(
                self.databases['tasks'],
                filter_conditions=filter_conditions,
                sorts=[{"property": "Created", "direction": "descending"}]
            )
            
        except Exception as e:
            logger.error(f"Recent tasks error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def save_chat_memory(self, conversation_id: str, summary: str, 
                        importance: int, tags: List[str] = None) -> Dict:
        """Save important conversation memories to Notion."""
        if not self.databases['chat_memory']:
            return {'success': False, 'error': 'Chat memory database ID not configured'}
        
        try:
            properties = {
                "Conversation ID": {"rich_text": [{"text": {"content": conversation_id}}]},
                "Summary": {"rich_text": [{"text": {"content": summary}}]},
                "Importance": {"number": importance},
                "Date": {"date": {"start": datetime.now().isoformat()}}
            }
            
            if tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag} for tag in tags]
                }
            
            result = self.client.pages.create(
                parent={"database_id": self.databases['chat_memory']},
                properties=properties
            )
            
            return {
                'success': True,
                'memory_id': result['id'],
                'message': 'Chat memory saved successfully'
            }
            
        except Exception as e:
            logger.error(f"Chat memory save error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_title(self, item: Dict) -> str:
        """Extract title from a Notion item."""
        if 'title' in item.get('properties', {}):
            title_prop = item['properties']['title']
            if title_prop.get('title'):
                return ''.join([t.get('plain_text', '') for t in title_prop['title']])
        
        # Fallback to item title if it exists
        if item.get('title'):
            return ''.join([t.get('plain_text', '') for t in item['title']])
        
        return 'Untitled'
    
    def _format_database_page(self, page: Dict) -> Dict:
        """Format a database page for API response."""
        formatted = {
            'id': page['id'],
            'url': page.get('url', ''),
            'created_time': page.get('created_time', ''),
            'last_edited_time': page.get('last_edited_time', ''),
            'properties': {}
        }
        
        # Extract and format properties
        for prop_name, prop_data in page.get('properties', {}).items():
            prop_type = prop_data.get('type')
            
            if prop_type == 'title':
                formatted['properties'][prop_name] = self._extract_title(page)
            elif prop_type == 'rich_text':
                formatted['properties'][prop_name] = ''.join([
                    t.get('plain_text', '') for t in prop_data.get('rich_text', [])
                ])
            elif prop_type == 'select':
                select_data = prop_data.get('select')
                formatted['properties'][prop_name] = select_data.get('name') if select_data else None
            elif prop_type == 'multi_select':
                formatted['properties'][prop_name] = [
                    item.get('name') for item in prop_data.get('multi_select', [])
                ]
            elif prop_type == 'date':
                date_data = prop_data.get('date')
                formatted['properties'][prop_name] = date_data.get('start') if date_data else None
            elif prop_type == 'number':
                formatted['properties'][prop_name] = prop_data.get('number')
            elif prop_type == 'checkbox':
                formatted['properties'][prop_name] = prop_data.get('checkbox')
            else:
                # For other types, just include the raw data
                formatted['properties'][prop_name] = prop_data
        
        return formatted

# Global instance
notion_service = NotionService()

# Convenience functions for main.py
def search_notion(query: str, limit: int = 20) -> Dict:
    return notion_service.search_all_content(query, limit)

def get_notion_databases() -> Dict:
    return notion_service.get_all_databases()

def create_notion_task(title: str, description: str = "", project: str = "", 
                      priority: str = "Medium", due_date: Optional[str] = None) -> Dict:
    return notion_service.create_task(title, description, project, priority, due_date)

def get_recent_notion_tasks(days: int = 7, status_filter: str = None) -> Dict:
    return notion_service.get_recent_tasks(days, status_filter)
