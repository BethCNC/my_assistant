#!/usr/bin/env python3
"""
Test script for Notion API connection.

This script verifies that the Notion integration is working correctly
by testing the API connection and accessing the configured databases.
"""
import os
import sys
import json
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the NotionMedicalClient class
from src.notion_integration.notion_client import NotionMedicalClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notion_test")

def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser for CLI arguments."""
    parser = argparse.ArgumentParser(description='Test Notion API connection')
    parser.add_argument(
        '--config-file',
        type=str,
        default='config/notion_config.json',
        help='Path to Notion configuration file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    return parser

def test_notion_connection(config_file, verbose=False):
    """
    Test the connection to the Notion API.
    
    Args:
        config_file: Path to the Notion configuration file
        verbose: Whether to display verbose output
    
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Initialize the Notion client
        logger.info("Initializing Notion client...")
        client = NotionMedicalClient(config_file=config_file)
        
        # Test user information
        logger.info("Retrieving user information...")
        try:
            _ = client.client.users.me()
            logger.info("✓ Successfully authenticated with Notion API")
        except Exception as e:
            logger.error(f"✗ Error authenticating with Notion API: {str(e)}")
            return False
        
        # Test database access
        logger.info("Testing database access...")
        database_types = list(client.database_ids.keys())
        for db_type in database_types:
            db_id = client.database_ids.get(db_type)
            if not db_id:
                logger.warning(f"- No database ID found for {db_type}, skipping...")
                continue
                
            logger.info(f"- Testing access to {db_type} database ({db_id})...")
            try:
                # Fetch database to check access
                db_response = client.client.databases.retrieve(database_id=db_id)
                logger.info(f"  ✓ Successfully accessed {db_type} database")
                
                # Show database structure in verbose mode
                if verbose:
                    logger.info(f"  Database structure:")
                    try:
                        # Access properties safely
                        properties = db_response.get("properties", {}) if isinstance(db_response, dict) else getattr(db_response, "properties", {})
                        for prop_name, prop_data in properties.items():
                            prop_type = prop_data.get("type", "unknown") if isinstance(prop_data, dict) else "unknown"
                            logger.info(f"    - {prop_name}: {prop_type}")
                    except Exception as e:
                        logger.warning(f"    Could not retrieve database structure: {str(e)}")
                    
            except Exception as e:
                logger.error(f"  ✗ Error accessing {db_type} database: {str(e)}")
                return False
        
        logger.info("All tests passed! Notion integration is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Notion connection: {str(e)}")
        return False

def main():
    """Main entry point for the script."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Test the Notion connection
    success = test_notion_connection(args.config_file, args.verbose)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 