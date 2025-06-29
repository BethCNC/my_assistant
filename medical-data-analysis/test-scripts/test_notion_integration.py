#!/usr/bin/env python3
"""
Test Notion Integration

This script tests the Notion integration components by:
1. Extracting entities from sample medical data
2. Mapping them to Notion properties
3. Optionally syncing them to Notion (if NOTION_TOKEN is set)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup test environment and check required components"""
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required for entity extraction")
        return False
    
    # Create data directory structure if it doesn't exist
    data_dir = Path("data")
    input_dir = data_dir / "input"
    output_dir = data_dir / "processed_data"
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if sample data exists
    sample_file = input_dir / "sample_visit.txt"
    if not sample_file.exists():
        logger.error(f"Sample data file not found: {sample_file}")
        logger.info("Please create a sample medical document in data/input/sample_visit.txt")
        return False
    
    # Check if config files exist
    config_dir = Path("config")
    notion_config = config_dir / "notion_config.json"
    field_mapping = config_dir / "notion_field_mapping.json"
    
    if not notion_config.exists() or not field_mapping.exists():
        logger.error(f"Configuration files not found in {config_dir}")
        logger.info("Please create notion_config.json and notion_field_mapping.json in the config directory")
        return False
    
    return True

def test_entity_extraction():
    """Test entity extraction from sample data"""
    from src.notion_integration.entity_extractor import EntityExtractor, extract_entities_from_document
    
    logger.info("Testing entity extraction...")
    
    sample_file = Path("data/input/sample_visit.txt")
    
    try:
        # Create entity extractor
        extractor = EntityExtractor()
        
        # Extract entities
        entities = extract_entities_from_document(
            str(sample_file),
            extractor,
            document_date="2023-05-01",  # Example date
            document_type="visit"
        )
        
        # Save extracted entities to JSON
        output_file = Path("data/processed_data/sample_visit_extracted.json")
        with open(output_file, 'w') as f:
            json.dump(entities, f, indent=2)
        
        logger.info(f"Extracted entities saved to {output_file}")
        
        # Print summary of extracted entities
        entity_counts = {
            entity_type: len(entities.get(entity_type, [])) 
            for entity_type in ["appointments", "medications", "diagnoses", "symptoms", "providers"]
        }
        
        logger.info("Extraction summary:")
        for entity_type, count in entity_counts.items():
            logger.info(f"  - {entity_type.capitalize()}: {count}")
        
        return entities
    
    except Exception as e:
        logger.error(f"Error during entity extraction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def test_notion_mapping(entities):
    """Test mapping extracted entities to Notion properties"""
    from src.notion_integration.notion_entity_mapper import NotionEntityMapper
    
    if not entities:
        logger.error("No entities to map")
        return False
    
    logger.info("Testing Notion entity mapping...")
    
    try:
        # Create entity mapper
        mapper = NotionEntityMapper()
        
        # Test mapping for each entity type
        for entity_type, entity_list in entities.items():
            if not entity_list:
                logger.info(f"No {entity_type} to map")
                continue
            
            # Get the first entity of this type
            sample_entity = entity_list[0]
            
            # Map to Notion properties
            notion_properties = mapper.map_entity_to_notion_properties(sample_entity, entity_type)
            
            if notion_properties:
                logger.info(f"Successfully mapped {entity_type} to Notion properties")
                
                # Print sample mapping
                logger.info(f"Sample {entity_type} mapping:")
                db_name = mapper.get_notion_database(entity_type)
                logger.info(f"  - Database: {db_name}")
                logger.info(f"  - Properties: {list(notion_properties.keys())}")
            else:
                logger.warning(f"Failed to map {entity_type} to Notion properties")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during Notion mapping: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_notion_client():
    """Test Notion client if token is available"""
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        logger.warning("NOTION_TOKEN not set, skipping Notion client test")
        return False
    
    logger.info("Testing Notion client...")
    
    try:
        from src.notion_integration.notion_client import NotionClient
        
        # Create Notion client
        client = NotionClient(token=notion_token)
        
        # Get available databases
        databases = client.get_all_databases()
        
        if databases:
            logger.info(f"Successfully connected to Notion. Found {len(databases)} databases:")
            for name, db_id in databases.items():
                logger.info(f"  - {name}: {db_id}")
        else:
            logger.warning("No databases found in Notion workspace")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing Notion client: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_sync_to_notion(entities):
    """Test syncing entities to Notion if token is available"""
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        logger.warning("NOTION_TOKEN not set, skipping Notion sync test")
        return False
    
    if not entities:
        logger.error("No entities to sync")
        return False
    
    logger.info("Testing sync to Notion...")
    
    try:
        from src.notion_integration.notion_client import NotionClient
        from src.notion_integration.notion_entity_mapper import NotionEntityMapper
        
        # Create Notion client and entity mapper
        client = NotionClient(token=notion_token)
        mapper = NotionEntityMapper()
        
        # Choose one entity type with data for testing
        test_entity_type = None
        test_entity = None
        
        for entity_type, entity_list in entities.items():
            if entity_list:
                test_entity_type = entity_type
                test_entity = entity_list[0]
                break
        
        if not test_entity_type or not test_entity:
            logger.warning("No suitable entity found for testing")
            return False
        
        # Map entity to Notion properties
        properties = mapper.map_entity_to_notion_properties(test_entity, test_entity_type)
        
        # Get database ID
        db_name = mapper.get_notion_database(test_entity_type)
        db_id = client.get_database(db_name)
        
        if not db_id:
            logger.error(f"Database not found for {test_entity_type} (name: {db_name})")
            return False
        
        # Add test marker
        if "title" in properties and "title" in properties["title"]:
            title_obj = properties["title"]["title"]
            if isinstance(title_obj, list) and title_obj:
                current_title = title_obj[0]["text"]["content"]
                title_obj[0]["text"]["content"] = f"[TEST] {current_title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Create page in Notion
        logger.info(f"Creating test page in {db_name}...")
        result = client.create_page(db_id, properties)
        
        if result and "id" in result:
            logger.info(f"Successfully created page in Notion: {result['id']}")
            logger.info(f"Test sync completed successfully")
            return True
        else:
            logger.warning("Failed to create page in Notion")
            return False
    
    except Exception as e:
        logger.error(f"Error syncing to Notion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main test function"""
    logger.info("Starting Notion integration tests...")
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed")
        return 1
    
    # Test entity extraction
    entities = test_entity_extraction()
    
    # Exit if extraction failed
    if not entities:
        logger.error("Entity extraction test failed")
        return 1
    
    # Test notion mapping
    if not test_notion_mapping(entities):
        logger.warning("Notion mapping test failed or had warnings")
    
    # Test Notion client
    test_notion_client()
    
    # Test sync to Notion
    test_sync_to_notion(entities)
    
    logger.info("Notion integration tests completed")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 