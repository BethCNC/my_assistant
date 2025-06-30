#!/usr/bin/env python3
"""
Notion Integration Config Verifier

This script verifies your Notion configuration by checking:
1. If your API token is valid
2. If all database IDs are valid and accessible
3. If the field mapping matches the database structure

Usage:
    python verify_notion_config.py --config config/notion_config.json --mapping config/notion_field_mapping.json
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from src.notion_integration.notion_client import NotionClient
from src.notion_integration.config import ConfigManager

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def verify_notion_token(token):
    """Verify the Notion API token is valid."""
    client = NotionClient(token)
    try:
        # Check if we can access the search API
        results = client.search("", {"object": "database"})
        print(f"✅ Notion API token is valid. Found {len(results)} databases.")
        return True
    except Exception as e:
        print(f"❌ Notion API token is invalid: {str(e)}")
        return False

def verify_database_access(client, database_id, database_name):
    """Verify database exists and is accessible."""
    try:
        database = client.get_database(database_id)
        title = database.get("title", [{"plain_text": "Unnamed"}])[0]["plain_text"]
        print(f"✅ Database '{database_name}' ({title}) is accessible")
        return database
    except Exception as e:
        print(f"❌ Unable to access database '{database_name}' ({database_id}): {str(e)}")
        return None

def verify_field_mappings(database, mapping, entity_type):
    """Verify field mappings match database schema."""
    if not database or not mapping:
        return False
    
    # Get database properties
    db_properties = database.get("properties", {})
    field_mapping = mapping.get(entity_type, {}).get("fields", {})
    
    # Check each mapped field exists in the database
    missing_fields = []
    for field_name, notion_field in field_mapping.items():
        # Skip relation fields for now
        if isinstance(notion_field, dict) and "relation" in notion_field:
            continue
            
        if notion_field not in db_properties and notion_field != "title":
            missing_fields.append(f"{field_name} -> {notion_field}")
    
    if missing_fields:
        print(f"❌ Missing fields in {entity_type} mapping:")
        for field in missing_fields:
            print(f"  - {field}")
        return False
    
    print(f"✅ All mapped fields for {entity_type} exist in the database")
    return True

def main():
    parser = argparse.ArgumentParser(description="Verify Notion configuration")
    parser.add_argument("--config", required=True, help="Path to Notion config JSON file")
    parser.add_argument("--mapping", required=True, help="Path to field mapping JSON file")
    args = parser.parse_args()
    
    # Load configuration files
    config = load_json_file(args.config)
    if not config:
        return
        
    mapping = load_json_file(args.mapping)
    if not mapping:
        return
    
    # Verify Notion token
    token = config.get("notion", {}).get("token")
    if not token or token == "your_notion_api_token_here":
        print("❌ Please set your Notion API token in the config file")
        return
        
    if not verify_notion_token(token):
        return
    
    # Create client
    client = NotionClient(token)
    
    # Verify database access and field mappings
    databases = config.get("notion", {}).get("databases", {})
    all_valid = True
    
    for db_name, db_id in databases.items():
        database = verify_database_access(client, db_id, db_name)
        if not database:
            all_valid = False
            continue
            
        # Find entity type for this database
        entity_type = None
        for entity, entity_config in mapping.items():
            if entity_config.get("notion_database") == db_name:
                entity_type = entity
                break
                
        if entity_type:
            if not verify_field_mappings(database, mapping, entity_type):
                all_valid = False
        else:
            print(f"❌ No entity mapping found for database '{db_name}'")
            all_valid = False
    
    # Test OpenAI API key if entity extraction is enabled
    openai_key = config.get("openai", {}).get("api_key")
    if openai_key == "your_openai_api_key_here":
        print("⚠️ Warning: OpenAI API key is not set. Entity extraction will not work.")
    
    # Final summary
    if all_valid:
        print("\n✅ Configuration verified successfully! You're ready to sync medical data to Notion.")
    else:
        print("\n❌ There were configuration issues that need to be fixed before syncing.")

if __name__ == "__main__":
    main() 