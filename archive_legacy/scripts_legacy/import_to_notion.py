#!/usr/bin/env python3
"""
Import formatted medical data to Notion databases.

This script takes formatted medical events and imports them to the
Notion medical calendar database, handling related entries as needed.
"""
import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.notion_integration.notion_client import NotionMedicalClient
except ImportError:
    logging.error("Could not import NotionMedicalClient. Make sure it exists in src/notion_integration/notion_client.py")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notion_import")

def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure an argument parser."""
    parser = argparse.ArgumentParser(
        description="Import formatted medical events to Notion"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="data/notion_formatted_events.json",
        help="Input file with Notion-formatted events (default: data/notion_formatted_events.json)"
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default="config/notion_config.json",
        help="Notion configuration file (default: config/notion_config.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually creating entries in Notion"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Batch size for API requests (default: 5)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)"
    )
    return parser

def load_json_file(file_path: str) -> Dict:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data as a dictionary
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def save_json_file(data: Dict, file_path: str) -> bool:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        file_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save data to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False

def find_or_create_related_entities(
    notion_client: NotionMedicalClient, 
    event: Dict[str, Any],
    database_types: List[str]
) -> Dict[str, Any]:
    """
    Find or create related entities (doctors, conditions, symptoms, medications).
    
    Args:
        notion_client: Notion client for API access
        event: Original event data
        database_types: Types of databases to process
        
    Returns:
        Dictionary of relation mappings by database type
    """
    relations = {}
    
    # Map of event fields to database types
    field_mapping = {
        "doctor": "medical_team",
        "related_diagnoses": "medical_conditions",
        "linked_symptoms": "symptoms",
        "medications": "medications"
    }
    
    for event_field, db_type in field_mapping.items():
        # Skip if database type is not requested
        if db_type not in database_types:
            continue
            
        # Skip if the event doesn't have this field or it's empty
        if event_field not in event or not event[event_field]:
            continue
            
        values = event[event_field]
        
        # Ensure values is a list
        if not isinstance(values, list):
            values = [values]
            
        # Find or create each value
        relation_ids = []
        for value in values:
            if value:  # Skip empty values
                try:
                    page_id = notion_client.find_or_create_entity(db_type, value)
                    if page_id:
                        relation_ids.append(page_id)
                except Exception as e:
                    logger.warning(f"Error processing {db_type} '{value}': {str(e)}")
        
        if relation_ids:
            relations[event_field] = relation_ids
    
    return relations

def update_event_with_relations(
    event_properties: Dict[str, Any],
    relations: Dict[str, List[str]],
    field_mapping: Dict[str, str]
) -> Dict[str, Any]:
    """
    Update event properties with relation IDs.
    
    Args:
        event_properties: Event properties dictionary
        relations: Dictionary of relation IDs by field name
        field_mapping: Mapping from internal fields to Notion properties
        
    Returns:
        Updated event properties
    """
    updated_properties = event_properties.copy()
    
    # Map of event fields to Notion property names
    relation_field_mapping = {
        "doctor": "doctor",
        "related_diagnoses": "related_diagnoses",
        "linked_symptoms": "linked_symptoms",
        "medications": "medications"
    }
    
    for event_field, relation_ids in relations.items():
        if event_field in relation_field_mapping and relation_field_mapping[event_field] in field_mapping:
            notion_property = field_mapping[relation_field_mapping[event_field]]
            updated_properties[notion_property] = {
                "relation": [{"id": page_id} for page_id in relation_ids]
            }
    
    return updated_properties

def import_events_to_notion(client, formatted_events, batch_size=10, delay=1.0):
    """
    Import formatted events to Notion.
    
    Args:
        client: NotionMedicalClient instance
        formatted_events: List of formatted event objects
        batch_size: Number of events to process in a batch
        delay: Delay between API calls in seconds
        
    Returns:
        Number of successfully imported events
    """
    # Track results
    successful_count = 0
    
    # Process in batches to avoid rate limits
    for i in range(0, len(formatted_events), batch_size):
        batch = formatted_events[i:i+batch_size]
        
        for event in batch:
            try:
                # Create the event in the medical calendar database
                response = client.create_database_item('medical_calendar', event['properties'])
                
                # Log the success
                event_name = event['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Unknown')
                logger.info(f"Created event: {event_name}")
                
                successful_count += 1
                
            except Exception as e:
                logger.error(f"Error creating event: {str(e)}")
        
        # Sleep between batches to avoid rate limits
        if i + batch_size < len(formatted_events):
            time.sleep(delay)
    
    return successful_count

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    args = setup_argument_parser()
    args = args.parse_args()
    
    try:
        # Load formatted events
        with open(args.input_file, 'r') as f:
            data = json.load(f)
            formatted_events = data.get('formatted_events', [])
        
        logger.info(f"Loaded {len(formatted_events)} formatted events from {args.input_file}")
        
        # Initialize Notion client
        client = NotionMedicalClient(config_file=args.config_file)
        
        # Import events to Notion
        imported_count = import_events_to_notion(client, formatted_events)
        
        logger.info(f"Successfully imported {imported_count} events to Notion")
        
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {args.input_file}")
        return 1
    except FileNotFoundError:
        logger.error(f"File not found: {args.input_file}")
        return 1
    except Exception as e:
        logger.exception(f"Error during import: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 