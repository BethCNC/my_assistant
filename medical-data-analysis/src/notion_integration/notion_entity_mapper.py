"""
Notion Entity Mapper

This module provides utilities for mapping extracted entities to Notion properties.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class NotionEntityMapper:
    """Maps extracted medical entities to Notion properties format"""
    
    def __init__(self, field_mapping_path: str = "config/notion_field_mapping.json"):
        """
        Initialize the mapper with field mappings
        
        Args:
            field_mapping_path: Path to the field mapping configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.field_mapping = self._load_field_mapping(field_mapping_path)
        
    def _load_field_mapping(self, field_mapping_path: str) -> Dict[str, Any]:
        """
        Load field mapping from a JSON file
        
        Args:
            field_mapping_path: Path to the field mapping file
            
        Returns:
            Field mapping dictionary
        """
        try:
            with open(field_mapping_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"Error loading field mapping from {field_mapping_path}: {str(e)}")
            # Return a minimal default mapping
            return self._get_default_mapping()
    
    def _get_default_mapping(self) -> Dict[str, Any]:
        """
        Get a default field mapping
        
        Returns:
            Default field mapping dictionary
        """
        return {
            "appointments": {
                "database": "Appointments",
                "fields": {
                    "title": {"type": "title", "source": "description"},
                    "date": {"type": "date", "source": "date"},
                    "provider": {"type": "rich_text", "source": "provider"},
                    "location": {"type": "rich_text", "source": "location"},
                    "notes": {"type": "rich_text", "source": "notes"}
                }
            },
            "medications": {
                "database": "Medications",
                "fields": {
                    "title": {"type": "title", "source": "name"},
                    "dosage": {"type": "rich_text", "source": "dosage"},
                    "frequency": {"type": "rich_text", "source": "frequency"},
                    "start_date": {"type": "date", "source": "start_date"},
                    "end_date": {"type": "date", "source": "end_date"},
                    "prescriber": {"type": "rich_text", "source": "prescriber"},
                    "notes": {"type": "rich_text", "source": "notes"}
                }
            },
            "diagnoses": {
                "database": "Diagnoses",
                "fields": {
                    "title": {"type": "title", "source": "name"},
                    "date": {"type": "date", "source": "date"},
                    "provider": {"type": "rich_text", "source": "provider"},
                    "status": {"type": "select", "source": "status"},
                    "notes": {"type": "rich_text", "source": "notes"}
                }
            },
            "symptoms": {
                "database": "Symptoms",
                "fields": {
                    "title": {"type": "title", "source": "name"},
                    "date": {"type": "date", "source": "date"},
                    "severity": {"type": "select", "source": "severity"},
                    "duration": {"type": "rich_text", "source": "duration"},
                    "related_diagnosis": {"type": "rich_text", "source": "related_diagnosis"},
                    "notes": {"type": "rich_text", "source": "notes"}
                }
            },
            "providers": {
                "database": "Providers",
                "fields": {
                    "title": {"type": "title", "source": "name"},
                    "specialty": {"type": "rich_text", "source": "specialty"},
                    "facility": {"type": "rich_text", "source": "facility"},
                    "phone": {"type": "phone_number", "source": "phone"},
                    "email": {"type": "email", "source": "email"},
                    "address": {"type": "rich_text", "source": "address"},
                    "notes": {"type": "rich_text", "source": "notes"}
                }
            }
        }
    
    def get_notion_database(self, entity_type: str) -> str:
        """
        Get the Notion database name for an entity type
        
        Args:
            entity_type: The entity type (e.g., "medications", "appointments")
        
        Returns:
            Notion database name
        """
        entity_mapping = self.field_mapping.get(entity_type, {})
        return entity_mapping.get("database", entity_type.capitalize())
    
    def map_entity_to_notion_properties(self, entity: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Map an entity to Notion properties
        
        Args:
            entity: The entity to map
            entity_type: The type of the entity
            
        Returns:
            Dictionary of Notion properties
        """
        if not entity:
            return {}
            
        # Get field mapping for this entity type
        entity_mapping = self.field_mapping.get(entity_type)
        if not entity_mapping or "fields" not in entity_mapping:
            self.logger.warning(f"No field mapping found for entity type: {entity_type}")
            return {}
            
        fields_mapping = entity_mapping.get("fields", {})
        properties = {}
        
        # Map each field according to the mapping
        for notion_field, field_config in fields_mapping.items():
            field_type = field_config.get("type")
            source_field = field_config.get("source")
            
            if not field_type or not source_field:
                continue
                
            # Get the value from the entity
            value = entity.get(source_field)
            
            # Skip if value is None or empty string
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
                
            # Map the value to the appropriate Notion property format
            properties[notion_field] = self._format_notion_property(value, field_type)
            
        return properties
    
    def _format_notion_property(self, value: Any, property_type: str) -> Dict[str, Any]:
        """
        Format a value for a Notion property
        
        Args:
            value: The value to format
            property_type: The Notion property type
            
        Returns:
            Formatted property value
        """
        if property_type == "title":
            return {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }
        elif property_type == "rich_text":
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }
        elif property_type == "number":
            try:
                return {"number": float(value)}
            except (ValueError, TypeError):
                return {"number": 0}
        elif property_type == "select":
            return {
                "select": {
                    "name": str(value)
                }
            }
        elif property_type == "multi_select":
            if isinstance(value, list):
                return {
                    "multi_select": [{"name": str(item)} for item in value]
                }
            else:
                return {
                    "multi_select": [{"name": str(value)}]
                }
        elif property_type == "date":
            # Handle various date formats and convert to Notion format
            try:
                if isinstance(value, str):
                    # Try to parse various date formats
                    formats = [
                        "%Y-%m-%d",        # ISO format: 2023-05-01
                        "%m/%d/%Y",        # US format: 05/01/2023
                        "%B %d, %Y"        # Long format: May 1, 2023
                    ]
                    
                    parsed_date = None
                    for date_format in formats:
                        try:
                            parsed_date = datetime.strptime(value, date_format)
                            break
                        except ValueError:
                            continue
                    
                    if parsed_date:
                        return {
                            "date": {
                                "start": parsed_date.strftime("%Y-%m-%d")
                            }
                        }
                
                # Default to original value if parsing fails
                return {
                    "date": {
                        "start": str(value)
                    }
                }
            except Exception as e:
                self.logger.warning(f"Error formatting date value '{value}': {str(e)}")
                return {
                    "date": None
                }
        elif property_type == "checkbox":
            # Convert various truthy values to boolean
            if isinstance(value, bool):
                return {"checkbox": value}
            elif isinstance(value, str):
                return {"checkbox": value.lower() in ["true", "yes", "y", "1"]}
            elif isinstance(value, (int, float)):
                return {"checkbox": value > 0}
            else:
                return {"checkbox": bool(value)}
        elif property_type == "url":
            return {"url": str(value)}
        elif property_type == "email":
            return {"email": str(value)}
        elif property_type == "phone_number":
            return {"phone_number": str(value)}
        else:
            # Fallback to rich_text for unsupported types
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            } 