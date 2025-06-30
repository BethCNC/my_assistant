#!/usr/bin/env python3
"""
Sync to Notion

This script syncs extracted medical entities to Notion databases.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
from src.notion_integration.notion_client import NotionClient
from src.notion_integration.notion_entity_mapper import NotionEntityMapper
from src.notion_integration.entity_extractor import EntityExtractor, extract_entities_from_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(description="Sync extracted medical entities to Notion")
    parser.add_argument("--input", "-i", type=str, required=True, 
                        help="Path to the input document or directory of documents")
    parser.add_argument("--output", "-o", type=str, default="data/processed_data",
                        help="Path to save processed data")
    parser.add_argument("--skip-extraction", action="store_true",
                        help="Skip extraction phase (use existing extracted data)")
    parser.add_argument("--skip-sync", action="store_true",
                        help="Skip syncing to Notion (extraction only)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Perform a dry run without actually syncing to Notion")
    return parser

def load_extracted_entities(json_path: str) -> Dict[str, Any]:
    """Load previously extracted entities from a JSON file"""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading extracted entities: {str(e)}")
        return {}

def extract_from_document(document_path: str, output_dir: str) -> str:
    """
    Extract entities from a document and save to JSON
    
    Args:
        document_path: Path to the document
        output_dir: Directory to save the extracted entities JSON
        
    Returns:
        Path to the extracted entities JSON file
    """
    # Create extractor
    extractor = EntityExtractor()
    
    # Extract document date from filename if possible
    document_filename = os.path.basename(document_path)
    document_date = None
    
    # Try to extract date from filename (e.g., 2023-04-15_visit.txt)
    date_formats = [
        "%Y-%m-%d",  # For 2023-04-15_visit.txt
        "%Y%m%d",    # For 20230415_visit.txt
        "%m-%d-%Y"   # For 04-15-2023_visit.txt
    ]
    
    for date_format in date_formats:
        try:
            parts = document_filename.split("_")[0].split(".")
            document_date = datetime.strptime(parts[0], date_format).strftime("%Y-%m-%d")
            break
        except (ValueError, IndexError):
            continue
    
    # Extract document type from filename if possible
    document_type = None
    if "_" in document_filename:
        try:
            document_type = document_filename.split("_")[1].split(".")[0]
        except IndexError:
            pass
    
    # Extract entities from document
    logger.info(f"Extracting entities from {document_path}")
    entities = extract_entities_from_document(
        document_path, 
        extractor, 
        document_date=document_date,
        document_type=document_type
    )
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save extracted entities to JSON
    output_basename = os.path.splitext(document_filename)[0]
    output_path = os.path.join(output_dir, f"{output_basename}_extracted.json")
    
    with open(output_path, 'w') as f:
        json.dump(entities, f, indent=2)
    
    logger.info(f"Saved extracted entities to {output_path}")
    return output_path

def sync_entities_to_notion(entities: Dict[str, Any], notion_client: NotionClient, 
                           entity_mapper: NotionEntityMapper, dry_run: bool = False) -> Dict[str, List[str]]:
    """
    Sync extracted entities to Notion
    
    Args:
        entities: Dictionary of extracted entities by type
        notion_client: Configured Notion client
        entity_mapper: Entity mapper for Notion properties
        dry_run: Whether to perform a dry run without actually syncing
        
    Returns:
        Dictionary of created page IDs by entity type
    """
    created_page_ids = {}
    
    for entity_type, entity_list in entities.items():
        if not entity_list:
            logger.info(f"No {entity_type} to sync")
            continue
            
        # Get the database name for this entity type
        db_name = entity_mapper.get_notion_database(entity_type)
        if not db_name:
            logger.warning(f"No database configured for entity type: {entity_type}")
            continue
            
        # Get the database ID
        db_id = notion_client.get_database(db_name)
        if not db_id:
            logger.warning(f"Database not found for {entity_type} (name: {db_name})")
            continue
            
        logger.info(f"Syncing {len(entity_list)} {entity_type} to Notion database {db_name}")
        
        # Track created pages for this entity type
        created_pages = []
        
        for entity in entity_list:
            # Map entity to Notion properties
            properties = entity_mapper.map_entity_to_notion_properties(entity, entity_type)
            
            # Check if entity already exists by title
            title_value = None
            for prop_name, prop_value in properties.items():
                if prop_name == "title" and "title" in prop_value:
                    try:
                        title_value = prop_value["title"][0]["text"]["content"]
                    except (KeyError, IndexError):
                        pass
                    break
            
            existing_page = None
            if title_value:
                existing_page = notion_client.find_by_title(db_id, title_value)
            
            if existing_page:
                # Update existing page
                logger.info(f"Updating existing {entity_type}: {title_value}")
                if not dry_run:
                    result = notion_client.update_page(existing_page["id"], properties)
                    if result:
                        created_pages.append(existing_page["id"])
            else:
                # Create new page
                logger.info(f"Creating new {entity_type}: {title_value or 'Untitled'}")
                if not dry_run:
                    result = notion_client.create_page(db_id, properties)
                    if result:
                        created_pages.append(result["id"])
        
        created_page_ids[entity_type] = created_pages
        logger.info(f"Synced {len(created_pages)} {entity_type} to Notion")
    
    return created_page_ids

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Check for Notion token if not skipping sync
    if not args.skip_sync and not os.getenv("NOTION_TOKEN"):
        logger.error("NOTION_TOKEN environment variable is required for syncing to Notion")
        logger.info("Set NOTION_TOKEN in .env file or run with --skip-sync flag")
        return 1
    
    # Process input path
    input_path = args.input
    
    if not os.path.exists(input_path):
        logger.error(f"Input path does not exist: {input_path}")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    
    # Process files
    json_paths = []
    
    if not args.skip_extraction:
        # Extract entities from document(s)
        if os.path.isdir(input_path):
            # Process all documents in the directory
            for filename in os.listdir(input_path):
                if filename.endswith((".txt", ".pdf", ".html", ".md", ".csv")):
                    document_path = os.path.join(input_path, filename)
                    json_path = extract_from_document(document_path, output_dir)
                    json_paths.append(json_path)
        else:
            # Process single document
            json_path = extract_from_document(input_path, output_dir)
            json_paths.append(json_path)
    else:
        # Use existing extracted data
        if os.path.isdir(input_path):
            for filename in os.listdir(input_path):
                if filename.endswith(".json"):
                    json_paths.append(os.path.join(input_path, filename))
        elif input_path.endswith(".json"):
            json_paths.append(input_path)
        else:
            logger.error("Input must be a JSON file when using --skip-extraction")
            return 1
    
    # Skip sync if requested
    if args.skip_sync:
        logger.info("Skipping sync to Notion")
        return 0
    
    # Create Notion client and entity mapper
    notion_client = NotionClient()
    entity_mapper = NotionEntityMapper()
    
    # Process each extracted entities JSON
    for json_path in json_paths:
        logger.info(f"Processing {json_path}")
        entities = load_extracted_entities(json_path)
        
        if not entities:
            logger.warning(f"No entities found in {json_path}")
            continue
        
        # Sync entities to Notion
        created_page_ids = sync_entities_to_notion(
            entities, 
            notion_client, 
            entity_mapper,
            dry_run=args.dry_run
        )
        
        # Save created page IDs back to the JSON file
        if not args.dry_run and created_page_ids:
            with open(json_path, 'r') as f:
                json_data = json.load(f)
            
            json_data["notion_sync"] = {
                "synced_at": datetime.now().isoformat(),
                "created_pages": created_page_ids
            }
            
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 