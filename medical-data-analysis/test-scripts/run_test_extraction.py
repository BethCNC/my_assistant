#!/usr/bin/env python3
"""
Run Test Extraction

This script performs test extraction on the sample medical data and optionally
syncs it to Notion if a token is provided.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path to help with imports
sys.path.append(str(Path(__file__).parent))

def extract_sample_data():
    """Run the entity extraction on sample data"""
    from src.notion_integration.entity_extractor import EntityExtractor
    
    # Sample file path
    sample_file = "data/input/sample_visit.txt"
    
    # Ensure the output directory exists
    os.makedirs("data/output", exist_ok=True)
    
    # Load the sample file
    with open(sample_file, "r") as f:
        content = f.read()
    
    # Extract entities
    logger.info(f"Extracting entities from {sample_file}...")
    extractor = EntityExtractor(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4o"
    )
    
    entities = extractor.extract_entities(
        text=content,
        document_date="2023-09-15",  # Sample date
        document_type="Clinical Visit"
    )
    
    # Save the entities to a file
    output_file = "data/output/extracted_entities.json"
    with open(output_file, "w") as f:
        json.dump(entities, f, indent=2)
    
    logger.info(f"Entities extracted and saved to {output_file}")
    
    # Extract structured entities
    structured_entities = {}
    
    # Add structured entities by type
    for entity_type in ["conditions", "medications", "symptoms", "providers", "appointments"]:
        structured_entities[entity_type] = []
        
        # Find entities of this type if they exist in the response
        if entities and isinstance(entities, dict) and entity_type in entities:
            if entities[entity_type] and isinstance(entities[entity_type], list):
                for entity in entities[entity_type]:
                    structured_entities[entity_type].append(entity)
    
    # Save the structured entities
    structured_output = "data/output/structured_entities.json"
    with open(structured_output, "w") as f:
        json.dump(structured_entities, f, indent=2)
    
    logger.info(f"Structured entities saved to {structured_output}")
    return structured_entities

def sync_to_notion(structured_entities):
    """Sync the extracted entities to Notion"""
    logger.info("Syncing extracted entities to Notion...")
    from src.notion_integration.notion_client import NotionClient
    
    # Create a minimal NotionEntityMapper for this script
    class NotionEntityMapper:
        def __init__(self, field_mapping):
            self.field_mapping = field_mapping
            
        def map_entity_to_notion_properties(self, entity, entity_type):
            """Map entity fields to Notion properties based on field mapping"""
            if entity_type not in self.field_mapping:
                return {}
                
            mapping = self.field_mapping[entity_type]
            props = {}
            
            # Map basic properties
            for entity_field, notion_field in mapping.get("fields", {}).items():
                if entity_field in entity:
                    props[notion_field] = {"title": [{"text": {"content": str(entity[entity_field])}}]}
                    
            return props
    
    # Get Notion token
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        logger.error("Notion token not found. Please set NOTION_TOKEN in your .env file.")
        return False
    
    # Get database IDs
    config_path = "config/notion_config.json"
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            
        db_ids = config["notion"]["databases"]
    except (json.JSONDecodeError, KeyError, IOError) as e:
        logger.error(f"Failed to load Notion database IDs: {str(e)}")
        return False
    
    # Load field mapping
    mapping_path = "config/notion_field_mapping.json"
    try:
        with open(mapping_path, "r") as f:
            field_mapping = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load field mapping: {str(e)}")
        return False
    
    # Initialize Notion client and mapper
    notion_client = NotionClient(notion_token)
    mapper = NotionEntityMapper(field_mapping)
    
    # Map and sync each entity type
    for entity_type, entities in structured_entities.items():
        if entity_type in field_mapping:
            db_name = field_mapping[entity_type].get("notion_database", entity_type)
            db_id = db_ids.get(db_name)
            
            if db_id:
                logger.info(f"Syncing {len(entities)} {entity_type} to Notion database {db_name}...")
                for entity in entities:
                    try:
                        # Map the entity to Notion format
                        notion_properties = mapper.map_entity_to_notion_properties(entity, entity_type)
                        
                        # Create a page in the Notion database
                        response = notion_client.create_page(db_id, notion_properties)
                        
                        entity_name = entity.get("name", "Unknown") if isinstance(entity, dict) else "Unknown"
                        if response:
                            logger.info(f"Successfully synced {entity_name} to Notion")
                        else:
                            logger.warning(f"Failed to sync {entity_name} to Notion")
                    except Exception as e:
                        entity_name = entity.get("name", "Unknown") if isinstance(entity, dict) else "Unknown"
                        logger.error(f"Error syncing entity {entity_name}: {str(e)}")
            else:
                logger.error(f"Database ID not found for {db_name}")
    
    logger.info("Notion sync completed")
    return True

def main():
    """Main function to run the extraction and optionally sync to Notion"""
    parser = argparse.ArgumentParser(description="Extract and sync medical data")
    parser.add_argument("--sync", action="store_true", help="Sync extracted data to Notion")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Extract sample data
    structured_entities = extract_sample_data()
    
    # Sync to Notion if requested
    if args.sync:
        if not os.getenv("NOTION_TOKEN"):
            logger.error("Notion token not found. Please set NOTION_TOKEN in your .env file.")
            return 1
        
        success = sync_to_notion(structured_entities)
        if not success:
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 