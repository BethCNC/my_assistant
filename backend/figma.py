"""
Figma API service for Beth's unified assistant.
Handles design file management, asset extraction, team collaboration, and design variables.
"""

import os
import requests
from typing import List, Dict, Optional, Any
import logging
from urllib.parse import urljoin
import base64
import json
from datetime import datetime

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
    
    def get_file_variables(self, file_key: str) -> Dict:
        """Get all variables from a Figma file including collections and modes."""
        try:
            url = urljoin(self.base_url, f"files/{file_key}/variables/local")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Figma Variables API error: {response.status_code}',
                    'details': response.text
                }
            
            data = response.json()
            
            # Organize variables by collection
            collections = {}
            variables_by_collection = {}
            
            # Process variable collections
            for collection_id, collection_data in data.get('meta', {}).get('variableCollections', {}).items():
                collection_name = collection_data.get('name', 'Unknown')
                collections[collection_id] = {
                    'id': collection_id,
                    'name': collection_name,
                    'modes': collection_data.get('modes', []),
                    'defaultModeId': collection_data.get('defaultModeId'),
                    'remote': collection_data.get('remote', False),
                    'hiddenFromPublishing': collection_data.get('hiddenFromPublishing', False),
                    'variables': []
                }
                variables_by_collection[collection_id] = []
            
            # Process variables
            for variable_id, variable_data in data.get('meta', {}).get('variables', {}).items():
                collection_id = variable_data.get('variableCollectionId')
                
                variable_info = {
                    'id': variable_id,
                    'name': variable_data.get('name'),
                    'description': variable_data.get('description', ''),
                    'type': variable_data.get('resolvedType'),
                    'scopes': variable_data.get('scopes', []),
                    'hiddenFromPublishing': variable_data.get('hiddenFromPublishing', False),
                    'values': {},
                    'aliases': {},
                    'raw_values': variable_data.get('valuesByMode', {})
                }
                
                # Process values by mode
                for mode_id, value in variable_data.get('valuesByMode', {}).items():
                    if isinstance(value, dict) and 'type' in value:
                        # This is an alias reference
                        if value['type'] == 'VARIABLE_ALIAS':
                            variable_info['aliases'][mode_id] = {
                                'type': 'alias',
                                'id': value.get('id'),
                                'raw': value
                            }
                        else:
                            variable_info['values'][mode_id] = value
                    else:
                        # Direct value
                        variable_info['values'][mode_id] = value
                
                if collection_id and collection_id in collections:
                    collections[collection_id]['variables'].append(variable_info)
                    variables_by_collection[collection_id].append(variable_info)
            
            return {
                'success': True,
                'collections': collections,
                'variables_by_collection': variables_by_collection,
                'total_collections': len(collections),
                'total_variables': len(data.get('meta', {}).get('variables', {})),
                'raw_data': data
            }
            
        except Exception as e:
            logger.error(f"Get file variables error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_variables_documentation(self, file_key: str, output_format: str = 'markdown') -> Dict:
        """Generate comprehensive documentation for all variable collections."""
        try:
            variables_data = self.get_file_variables(file_key)
            
            if not variables_data['success']:
                return variables_data
            
            collections = variables_data['collections']
            documentation = {
                'primitives': [],
                'alias': [],
                'semantics': [],
                'other': []
            }
            
            # Categorize collections
            for collection_id, collection in collections.items():
                collection_name = collection['name'].lower()
                
                if 'primitive' in collection_name or 'base' in collection_name:
                    category = 'primitives'
                elif 'alias' in collection_name or 'token' in collection_name:
                    category = 'alias'
                elif 'semantic' in collection_name or 'theme' in collection_name:
                    category = 'semantics'
                else:
                    category = 'other'
                
                documentation[category].append(collection)
            
            # Generate markdown documentation
            if output_format == 'markdown':
                markdown_content = self._generate_markdown_documentation(documentation, file_key)
                return {
                    'success': True,
                    'documentation': documentation,
                    'markdown': markdown_content,
                    'collections_count': len(collections)
                }
            
            return {
                'success': True,
                'documentation': documentation,
                'collections_count': len(collections)
            }
            
        except Exception as e:
            logger.error(f"Generate variables documentation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_markdown_documentation(self, documentation: Dict, file_key: str) -> str:
        """Generate markdown documentation for variable collections."""
        
        markdown = f"""# Design System Variables Documentation

**File Key:** `{file_key}`  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        # Process each category
        for category, collections in documentation.items():
            if not collections:
                continue
                
            category_title = category.title()
            markdown += f"## {category_title} Collections\n\n"
            
            for collection in collections:
                markdown += f"### {collection['name']}\n\n"
                
                # Collection metadata
                markdown += f"- **ID:** `{collection['id']}`\n"
                markdown += f"- **Variables Count:** {len(collection['variables'])}\n"
                markdown += f"- **Modes:** {len(collection['modes'])}\n"
                
                if collection.get('hiddenFromPublishing'):
                    markdown += f"- **Status:** Hidden from publishing\n"
                
                markdown += "\n"
                
                # Modes information
                if collection['modes']:
                    markdown += "#### Modes\n\n"
                    for mode in collection['modes']:
                        mode_indicator = " (Default)" if mode['modeId'] == collection.get('defaultModeId') else ""
                        markdown += f"- **{mode['name']}**{mode_indicator}: `{mode['modeId']}`\n"
                    markdown += "\n"
                
                # Variables table
                if collection['variables']:
                    markdown += "#### Variables\n\n"
                    markdown += "| Name | Type | Description | Values/Aliases |\n"
                    markdown += "|------|------|-------------|----------------|\n"
                    
                    for variable in collection['variables']:
                        name = variable['name']
                        var_type = variable.get('type', 'Unknown')
                        description = variable.get('description', '').replace('\n', ' ')[:100]
                        if len(description) > 100:
                            description += "..."
                        
                        # Format values/aliases
                        values_info = []
                        
                        # Direct values
                        for mode_id, value in variable.get('values', {}).items():
                            mode_name = next((m['name'] for m in collection['modes'] if m['modeId'] == mode_id), mode_id)
                            if isinstance(value, dict):
                                if 'r' in value and 'g' in value and 'b' in value:
                                    # Color value
                                    r = int(value['r'] * 255)
                                    g = int(value['g'] * 255)
                                    b = int(value['b'] * 255)
                                    a = value.get('a', 1)
                                    values_info.append(f"{mode_name}: rgba({r},{g},{b},{a})")
                                else:
                                    values_info.append(f"{mode_name}: {str(value)[:50]}")
                            else:
                                values_info.append(f"{mode_name}: {str(value)}")
                        
                        # Aliases
                        for mode_id, alias in variable.get('aliases', {}).items():
                            mode_name = next((m['name'] for m in collection['modes'] if m['modeId'] == mode_id), mode_id)
                            values_info.append(f"{mode_name}: →alias({alias.get('id', 'unknown')})")
                        
                        values_display = "<br>".join(values_info[:3])  # Limit to 3 entries
                        if len(values_info) > 3:
                            values_display += f"<br>... +{len(values_info)-3} more"
                        
                        markdown += f"| `{name}` | {var_type} | {description} | {values_display} |\n"
                    
                    markdown += "\n"
                
                markdown += "---\n\n"
        
        # Summary section
        total_collections = sum(len(collections) for collections in documentation.values())
        total_variables = sum(len(collection['variables']) for collections in documentation.values() for collection in collections)
        
        markdown += f"""## Summary

- **Total Collections:** {total_collections}
- **Total Variables:** {total_variables}
- **Primitives Collections:** {len(documentation['primitives'])}
- **Alias Collections:** {len(documentation['alias'])}
- **Semantics Collections:** {len(documentation['semantics'])}
- **Other Collections:** {len(documentation['other'])}

---

*Generated by Beth's Assistant Design System Documentation Tool*
"""
        
        return markdown

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
