#!/usr/bin/env python3
"""
Notion Integration Setup Test

This script tests your Notion integration setup by validating your configuration,
checking API connectivity, and verifying database access.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.notion_integration.notion_client import NotionClient
from src.notion_integration.config import ConfigManager
from src.notion_integration.notion_database_schema import (
    NotionDatabaseType, get_schema_for_database
)

def test_config_file(config_path):
    """Test configuration file loading"""
    logger.info("Testing configuration file...")
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check for required keys
        if 'notion' not in config:
            logger.error("Missing 'notion' section in config file")
            return False
            
        if 'token' not in config['notion']:
            logger.error("Missing Notion API token in config file")
            return False
            
        if 'databases' not in config['notion']:
            logger.error("Missing database IDs in config file")
            return False
            
        # Check if at least one database ID is provided
        if not any(config['notion']['databases'].values()):
            logger.error("No database IDs provided in config file")
            return False
            
        # Check OpenAI config for entity extraction
        if 'openai' not in config:
            logger.warning("Missing 'openai' section in config file (required for entity extraction)")
        elif 'api_key' not in config['openai'] or not config['openai']['api_key']:
            logger.warning("Missing OpenAI API key (required for entity extraction)")
        
        logger.info("Configuration file is valid")
        return True
        
    except Exception as e:
        logger.error(f"Error parsing configuration file: {e}")
        return False

def test_notion_api(config_path):
    """Test Notion API connectivity"""
    logger.info("Testing Notion API connection...")
    
    config_manager = ConfigManager(config_path)
    notion_token = config_manager.get('notion.token')
    
    if not notion_token:
        logger.error("No Notion API token found in configuration")
        return False
    
    notion_client = NotionClient(notion_token)
    
    try:
        # Test the API with a simple search query
        results = notion_client.search("", {"filter": {"value": "page", "property": "object"}})
        logger.info(f"Successfully connected to Notion API")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Notion API: {e}")
        return False

def test_database_access(config_path):
    """Test access to Notion databases"""
    logger.info("Testing Notion database access...")
    
    config_manager = ConfigManager(config_path)
    notion_token = config_manager.get('notion.token')
    
    if not notion_token:
        logger.error("No Notion API token found in configuration")
        return False
    
    notion_client = NotionClient(notion_token)
    databases = config_manager.get('notion.databases', {})
    
    if not databases:
        logger.error("No database IDs configured")
        return False
    
    success = True
    
    for db_type, db_id in databases.items():
        if not db_id:
            logger.warning(f"No database ID provided for {db_type}")
            continue
            
        logger.info(f"Testing access to {db_type} database...")
        
        try:
            # Try to get database info
            db_info = notion_client.get_database(db_id)
            logger.info(f"Successfully accessed {db_type} database: {db_info.get('title', [{'plain_text': 'Unnamed'}])[0]['plain_text']}")
            
            # Check database schema
            schema = get_schema_for_database(db_type)
            if schema:
                properties = db_info.get('properties', {})
                
                # Check for required properties
                missing_props = []
                for prop_name, prop_info in schema.properties.items():
                    if prop_info.get('required', False) and prop_name not in properties:
                        missing_props.append(prop_name)
                
                if missing_props:
                    logger.warning(f"Missing required properties in {db_type} database: {', '.join(missing_props)}")
                    success = False
            
        except Exception as e:
            logger.error(f"Failed to access {db_type} database: {e}")
            success = False
    
    return success

def test_document_directory(input_dir):
    """Test if the document directory exists and contains files"""
    logger.info(f"Testing document directory: {input_dir}")
    
    if not os.path.exists(input_dir):
        logger.warning(f"Document directory not found: {input_dir}")
        logger.info(f"Creating directory: {input_dir}")
        os.makedirs(input_dir, exist_ok=True)
        return False
    
    files = list(Path(input_dir).glob('*.*'))
    
    if not files:
        logger.warning(f"No files found in document directory: {input_dir}")
        return False
    
    logger.info(f"Found {len(files)} files in document directory")
    for file in files[:5]:  # Show only the first 5 files
        logger.info(f"  - {file.name}")
    
    if len(files) > 5:
        logger.info(f"  - ... and {len(files) - 5} more")
    
    return True

def main():
    """Main entry point for the script"""
    logger.info("=== Testing Notion Integration Setup ===")
    
    config_path = "config/notion_config.json"
    input_dir = "data/input"
    
    config_ok = test_config_file(config_path)
    api_ok = test_notion_api(config_path) if config_ok else False
    db_ok = test_database_access(config_path) if api_ok else False
    dir_ok = test_document_directory(input_dir)
    
    logger.info("\n=== Setup Test Results ===")
    logger.info(f"Configuration file: {'✅ PASSED' if config_ok else '❌ FAILED'}")
    logger.info(f"Notion API connection: {'✅ PASSED' if api_ok else '❌ FAILED'}")
    logger.info(f"Database access: {'✅ PASSED' if db_ok else '❌ FAILED or WARNINGS'}")
    logger.info(f"Document directory: {'✅ PASSED' if dir_ok else '❌ EMPTY'}")
    
    if all([config_ok, api_ok, db_ok, dir_ok]):
        logger.info("\n✅ All tests passed! You're ready to run the integration.")
        return 0
    else:
        logger.warning("\n⚠️ Some tests failed. Please address the issues before running the integration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 