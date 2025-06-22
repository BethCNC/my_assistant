"""
Figma API service for Beth's unified assistant.
Handles design file management, asset extraction, and team collaboration.
"""

import os
import requests
from typing import List, Dict, Optional, Any
import logging
from urllib.parse import urljoin
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FigmaService:
    def __init__(self):
        self.token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.token:
            raise ValueError("FIGMA_ACCESS_TOKEN not found in environment variables")
        
        self.base_url = "https://api.figma.com/v1/"
        self.headers = {
            "X-Figma-Token": self.token,
            "Content-Type": "application/json"
        }
        
        self.team_id = os.getenv("FIGMA_TEAM_ID")  # Optional
    
    async def test_connection(self):
        """Test the Figma API connection."""
        try:
            # Try to get user info - simple API call to test connection
            url = urljoin(self.base_url, "me")
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Figma connection test failed: {e}")
            raise e
    
    def get_user_files(self) -> Dict:
        """Get all files accessible to the user."""
        try:
            url = urljoin(self.base_url, "files")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            files = data.get('files', [])
            
            formatted_files = []
            for file_data in files:
                formatted_file = {
                    'key': file_data.get('key'),
                    'name': file_data.get('name'),
                    'thumbnail_url': file_data.get('thumbnail_url'),
                    'last_modified': file_data.get('last_modified'),
                    'version': file_data.get('version')
                }
                formatted_files.append(formatted_file)
            
            return {
                'success': True,
                'files': formatted_files,
                'count': len(formatted_files)
            }
            
        except Exception as e:
            logger.error(f"Get user files error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_team_files(self, team_id: str = None) -> Dict:
        """Get files from a specific team."""
        team_id = team_id or self.team_id
        if not team_id:
            return {'success': False, 'error': 'No team ID provided'}
        
        try:
            url = urljoin(self.base_url, f"teams/{team_id}/projects")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            projects = data.get('projects', [])
            
            all_files = []
            for project in projects:
                project_files = self.get_project_files(project['id'])
                if project_files['success']:
                    for file_data in project_files['files']:
                        file_data['project_name'] = project.get('name')
                        all_files.append(file_data)
            
            return {
                'success': True,
                'files': all_files,
                'count': len(all_files),
                'projects_count': len(projects)
            }
            
        except Exception as e:
            logger.error(f"Get team files error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_project_files(self, project_id: str) -> Dict:
        """Get files from a specific project."""
        try:
            url = urljoin(self.base_url, f"projects/{project_id}/files")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            files = data.get('files', [])
            
            formatted_files = []
            for file_data in files:
                formatted_file = {
                    'key': file_data.get('key'),
                    'name': file_data.get('name'),
                    'thumbnail_url': file_data.get('thumbnail_url'),
                    'last_modified': file_data.get('last_modified'),
                    'version': file_data.get('version')
                }
                formatted_files.append(formatted_file)
            
            return {
                'success': True,
                'files': formatted_files,
                'count': len(formatted_files)
            }
            
        except Exception as e:
            logger.error(f"Get project files error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_file_details(self, file_key: str, version: str = None, 
                        node_ids: List[str] = None, depth: int = 1) -> Dict:
        """Get detailed information about a specific file."""
        try:
            url = urljoin(self.base_url, f"files/{file_key}")
            params = {'depth': depth}
            
            if version:
                params['version'] = version
            if node_ids:
                params['ids'] = ','.join(node_ids)
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            
            # Extract useful information
            file_info = {
                'name': data.get('name'),
                'version': data.get('version'),
                'last_modified': data.get('lastModified'),
                'thumbnail_url': data.get('thumbnailUrl'),
                'document': data.get('document', {}),
                'components': data.get('components', {}),
                'styles': data.get('styles', {})
            }
            
            return {
                'success': True,
                'file': file_info
            }
            
        except Exception as e:
            logger.error(f"Get file details error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_file_components(self, file_key: str) -> Dict:
        """Get all components from a file."""
        try:
            url = urljoin(self.base_url, f"files/{file_key}/components")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            components = data.get('meta', {}).get('components', [])
            
            formatted_components = []
            for comp in components:
                formatted_comp = {
                    'key': comp.get('key'),
                    'name': comp.get('name'),
                    'description': comp.get('description'),
                    'node_id': comp.get('node_id'),
                    'thumbnail_url': comp.get('thumbnail_url'),
                    'created_at': comp.get('created_at'),
                    'updated_at': comp.get('updated_at')
                }
                formatted_components.append(formatted_comp)
            
            return {
                'success': True,
                'components': formatted_components,
                'count': len(formatted_components)
            }
            
        except Exception as e:
            logger.error(f"Get file components error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def export_images(self, file_key: str, node_ids: List[str], 
                     format: str = 'png', scale: float = 2.0) -> Dict:
        """Export images from specific nodes in a file."""
        try:
            url = urljoin(self.base_url, f"images/{file_key}")
            params = {
                'ids': ','.join(node_ids),
                'format': format,
                'scale': scale
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            images = data.get('images', {})
            
            return {
                'success': True,
                'images': images,
                'count': len(images)
            }
            
        except Exception as e:
            logger.error(f"Export images error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_file_styles(self, file_key: str) -> Dict:
        """Get all styles (colors, text, effects) from a file."""
        try:
            url = urljoin(self.base_url, f"files/{file_key}/styles")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            styles = data.get('meta', {}).get('styles', [])
            
            formatted_styles = []
            for style in styles:
                formatted_style = {
                    'key': style.get('key'),
                    'name': style.get('name'),
                    'description': style.get('description'),
                    'node_id': style.get('node_id'),
                    'style_type': style.get('style_type'),
                    'created_at': style.get('created_at'),
                    'updated_at': style.get('updated_at')
                }
                formatted_styles.append(formatted_style)
            
            return {
                'success': True,
                'styles': formatted_styles,
                'count': len(formatted_styles)
            }
            
        except Exception as e:
            logger.error(f"Get file styles error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def search_files(self, query: str) -> Dict:
        """Search for files by name."""
        try:
            # Get all files first
            all_files_result = self.get_user_files()
            if not all_files_result['success']:
                return all_files_result
            
            # Filter by query
            matching_files = []
            for file_data in all_files_result['files']:
                if query.lower() in file_data['name'].lower():
                    matching_files.append(file_data)
            
            return {
                'success': True,
                'files': matching_files,
                'count': len(matching_files),
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Search files error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_recent_files(self, days: int = 7) -> Dict:
        """Get recently modified files."""
        try:
            from datetime import datetime, timedelta
            
            all_files_result = self.get_user_files()
            if not all_files_result['success']:
                return all_files_result
            
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_files = []
            
            for file_data in all_files_result['files']:
                if file_data.get('last_modified'):
                    try:
                        file_date = datetime.fromisoformat(
                            file_data['last_modified'].replace('Z', '+00:00')
                        )
                        if file_date >= cutoff_date:
                            recent_files.append(file_data)
                    except ValueError:
                        # Skip files with invalid date format
                        continue
            
            # Sort by last modified (newest first)
            recent_files.sort(
                key=lambda x: x.get('last_modified', ''), 
                reverse=True
            )
            
            return {
                'success': True,
                'files': recent_files,
                'count': len(recent_files),
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Get recent files error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def download_image(self, image_url: str) -> Dict:
        """Download an image from Figma and return base64 encoded data."""
        try:
            response = requests.get(image_url)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Failed to download image: {response.status_code}'
                }
            
            # Encode image as base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            content_type = response.headers.get('content-type', 'image/png')
            
            return {
                'success': True,
                'image_data': image_data,
                'content_type': content_type,
                'size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"Download image error: {str(e)}")
            return {'success': False, 'error': str(e)}

# Global instance
figma_service = FigmaService()

# Convenience functions for main.py
def get_figma_files() -> Dict:
    return figma_service.get_user_files()

def search_figma_files(query: str) -> Dict:
    return figma_service.search_files(query)

def get_figma_file_details(file_key: str) -> Dict:
    return figma_service.get_file_details(file_key)

def get_figma_components(file_key: str) -> Dict:
    return figma_service.get_file_components(file_key)

def export_figma_images(file_key: str, node_ids: List[str], 
                       format: str = 'png', scale: float = 2.0) -> Dict:
    return figma_service.export_images(file_key, node_ids, format, scale)

def get_recent_figma_files(days: int = 7) -> Dict:
    return figma_service.get_recent_files(days)
