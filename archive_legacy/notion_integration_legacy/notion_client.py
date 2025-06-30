#!/usr/bin/env python3
"""
Notion client setup and utility functions for the medical data project.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, cast
from notion_client import Client, APIResponseError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notion_client")

# Load environment variables
load_dotenv()

class NotionMedicalClient:
    """Client wrapper for interacting with Notion medical databases."""
    
    def __init__(self, config_file=None, config=None):
        """
        Initialize the NotionMedicalClient.
        
        Args:
            config_file: Path to the configuration file (JSON)
            config: Configuration dict, used if config_file is None
        """
        # Load environment variables from .env file if present
        try:
            load_dotenv()
        except ImportError:
            logger.warning("python-dotenv not found, skipping .env loading")
        
        # Get API token from environment
        self.api_token = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
        
        # Load configuration
        self.config = {}
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Error loading config file {config_file}: {e}")
                raise ValueError(f"Invalid configuration file: {e}")
        elif config:
            self.config = config
            
        # Get token from config if not in environment
        if not self.api_token and self.config and 'notion' in self.config and 'token' in self.config['notion']:
            config_token = self.config['notion']['token']
            if config_token and config_token != "NOTION_API_TOKEN_GOES_HERE":
                self.api_token = config_token
                
        # Ensure we have a valid token
        if not self.api_token:
            raise ValueError("No Notion API token found. Set NOTION_API_KEY or NOTION_TOKEN environment variable.")
        
        # Initialize the client
        self.client = Client(auth=self.api_token)
        
        # Get database IDs from config
        self.database_ids = {}
        if self.config and 'notion' in self.config and 'databases' in self.config['notion']:
            self.database_ids = self.config['notion']['databases']
        
        # Load field mappings
        with open("config/notion_field_mapping.json", "r") as f:
            self.field_mappings = json.load(f)
    
    def query_database(self, database_type: str, filter_params: Optional[Dict] = None) -> List[Dict]:
        """
        Query a database with optional filters.
        
        Args:
            database_type: Type of database (medical_calendar, medical_team, etc.)
            filter_params: Optional filter parameters
            
        Returns:
            List of database items
        """
        database_id = self.database_ids.get(database_type)
        if not database_id:
            raise ValueError(f"Unknown database type: {database_type}")
        
        query_params = {"database_id": database_id}
        if filter_params:
            query_params["filter"] = filter_params
        
        response = self.client.databases.query(**query_params)
        results = cast(Dict[str, Any], response)
        return results.get("results", [])
    
    def find_entity_by_name(self, database_type: str, name: str) -> Optional[str]:
        """
        Find an entity by name in a database.
        
        Args:
            database_type: Type of database (medical_team, medical_conditions, etc.)
            name: Name to search for
            
        Returns:
            Entity page ID if found, None otherwise
        """
        filter_params = {
            "property": "Name",
            "title": {
                "equals": name
            }
        }
        
        results = self.query_database(database_type, filter_params)
        
        if results:
            return results[0]["id"]
        return None
    
    def create_entity(self, database_type: str, name: str) -> str:
        """
        Create a new entity in a database.
        
        Args:
            database_type: Type of database (medical_team, medical_conditions, etc.)
            name: Name of the entity to create
            
        Returns:
            ID of the created page
        """
        database_id = self.database_ids.get(database_type)
        if not database_id:
            raise ValueError(f"Unknown database type: {database_type}")
        
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
        }
        
        response = self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        page_data = cast(Dict[str, Any], response)
        return page_data["id"]
    
    def find_or_create_entity(self, database_type: str, name: str) -> str:
        """
        Find an entity by name or create it if not found.
        
        Args:
            database_type: Type of database (medical_team, medical_conditions, etc.)
            name: Name to search for or create
            
        Returns:
            Entity page ID
        """
        entity_id = self.find_entity_by_name(database_type, name)
        
        if entity_id:
            return entity_id
        
        return self.create_entity(database_type, name)
    
    def create_calendar_entry(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new entry in the medical calendar database.
        
        Args:
            database_id: ID of the medical calendar database
            properties: Properties for the new entry
            
        Returns:
            Created page data
        """
        response = self.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        return cast(Dict[str, Any], response)
    
    def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a page with new properties.
        
        Args:
            page_id: ID of the page to update
            properties: Updated properties
            
        Returns:
            Updated page data
        """
        response = self.client.pages.update(
            page_id=page_id,
            properties=properties
        )
        
        return cast(Dict[str, Any], response)
    
    def get_database(self, db_name: str, query_filter: Optional[Dict] = None, 
                   sorts: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Get entries from a database with optional filters and sorting.
        
        Args:
            db_name: Database name (must match a key in the database config)
            query_filter: Optional filter conditions
            sorts: Optional sort conditions
            
        Returns:
            List of database entries
        """
        db_id = self.database_ids.get(db_name)
        if not db_id:
            raise ValueError(f"Database '{db_name}' not found in configuration")
            
        query_args = {"database_id": db_id}
        
        if query_filter:
            query_args["filter"] = query_filter
            
        if sorts:
            query_args["sorts"] = sorts
            
        response = self.client.databases.query(**query_args)
        results = cast(Dict[str, Any], response)
        return results.get("results", [])
    
    def create_page(self, db_name: str, properties: Dict) -> Dict:
        """
        Create a new page in a database.
        
        Args:
            db_name: Database name (must match a key in the database config)
            properties: Page properties
            
        Returns:
            The created page object
        """
        db_id = self.database_ids.get(db_name)
        if not db_id:
            raise ValueError(f"Database '{db_name}' not found in configuration")
            
        response = self.client.pages.create(
            parent={"database_id": db_id},
            properties=properties
        )
        
        return cast(Dict[str, Any], response)
    
    def format_properties(self, db_name: str, data: Dict) -> Dict:
        """
        Format properties for a database according to its field mapping.
        
        Args:
            db_name: Database name
            data: Raw data to format
            
        Returns:
            Dictionary with Notion-formatted properties
        """
        if db_name not in self.field_mappings:
            raise ValueError(f"No field mapping found for '{db_name}'")
            
        mapping = self.field_mappings[db_name]
        properties = {}
        
        for field, notion_field in mapping.items():
            if field in data and data[field] is not None:
                # Format according to Notion property types
                # This is a simplified example - expand as needed
                properties[notion_field] = self._format_field_value(data[field])
                
        return properties
        
    def _format_field_value(self, value: Any) -> Dict:
        """
        Format a field value according to its type.
        This is a simplified implementation - expand with proper Notion formatting.
        
        Args:
            value: Value to format
            
        Returns:
            Notion-formatted value
        """
        if isinstance(value, str):
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": value
                        }
                    }
                ]
            }
        elif isinstance(value, (int, float)):
            return {"number": value}
        elif isinstance(value, bool):
            return {"checkbox": value}
        elif isinstance(value, list):
            # Simple handling for multi-select
            return {
                "multi_select": [{"name": item} for item in value]
            }
        else:
            # Default to string conversion
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }
    
    def find_or_create_relation(self, db_name: str, title: str) -> str:
        """
        Find an entity by title or create it if it doesn't exist.
        Useful for creating relations.
        
        Args:
            db_name: The database name to search in
            title: The title of the entity to find
            
        Returns:
            Page ID of the found or created entity
        """
        # Search for the entity
        filter_obj = {
            "property": "Name",
            "title": {
                "equals": title
            }
        }
        
        results = self.get_database(db_name, query_filter=filter_obj)
        
        if results:
            # Return the ID of the first matching result
            return results[0]["id"]
        
        # Entity not found, create it
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        created = self.create_page(db_name, properties)
        return created["id"]
    
    def map_internal_to_notion(self, db_name: str, internal_data: Dict) -> Dict:
        """
        Map internal data fields to Notion property format.
        
        Args:
            db_name: The database name for field mapping
            internal_data: Dictionary with internal field names
            
        Returns:
            Dictionary with Notion-formatted properties
        """
        if db_name not in self.field_mappings:
            raise ValueError(f"No field mapping found for '{db_name}'")
            
        mapping = self.field_mappings[db_name]
        properties = {}
        
        for internal_field, value in internal_data.items():
            if internal_field not in mapping:
                continue
                
            notion_field = mapping[internal_field]
            
            # Add proper typing based on field name and value type
            if internal_field == "name":
                properties[notion_field] = {
                    "title": [{"text": {"content": value}}]
                }
            elif "date" in internal_field.lower():
                properties[notion_field] = {"date": {"start": value}}
            elif isinstance(value, (int, float)):
                properties[notion_field] = {"number": value}
            elif isinstance(value, bool):
                properties[notion_field] = {"checkbox": value}
            elif internal_field in ["type", "role", "active", "affiliation"]:
                properties[notion_field] = {"select": {"name": value}}
            elif internal_field in ["frequency"]:
                # Handle multi-select
                multi_values = value if isinstance(value, list) else [value]
                properties[notion_field] = {
                    "multi_select": [{"name": v} for v in multi_values]
                }
            elif "doctor" in internal_field or "prescribed_by" in internal_field:
                # Handle single relation
                if value:
                    properties[notion_field] = {"relation": [{"id": value}]}
            elif internal_field in ["related_diagnoses", "linked_symptoms", 
                                  "medications", "treating", "prescribing",
                                  "to_treat", "related_events"]:
                # Handle multi-relations
                if value:
                    relation_ids = value if isinstance(value, list) else [value]
                    properties[notion_field] = {
                        "relation": [{"id": rel_id} for rel_id in relation_ids]
                    }
            else:
                # Default to rich text for other fields
                properties[notion_field] = {
                    "rich_text": [{"text": {"content": str(value)}}]
                }
                
        return properties
    
    def create_database_item(self, database_type, properties):
        """
        Create a new item in the specified database.
        
        Args:
            database_type: The type of database (e.g., 'medical_calendar')
            properties: The properties for the new item
            
        Returns:
            The created page object
        """
        # Get the database ID from the configuration
        database_id = self.database_ids.get(database_type)
        if not database_id:
            raise ValueError(f"Unknown database type: {database_type}")
        
        # Create the item in the database
        try:
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            return response
        except APIResponseError as e:
            logger.error(f"Error creating item in {database_type} database: {e}")
            raise 