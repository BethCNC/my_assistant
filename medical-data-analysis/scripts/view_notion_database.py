#!/usr/bin/env python3
"""
Notion Database Inspector

This script inspects an existing Notion database to show its structure,
which helps with properly configuring the integration.
"""

import sys
import json
import os
from src.notion_integration.notion_client import NotionClient

def inspect_database(token, database_id):
    """Inspect a Notion database and print its structure."""
    client = NotionClient(token)
    
    try:
        # Get database
        database = client.get_database(database_id)
        
        # Print basic info
        print("\n--- DATABASE INFO ---")
        title = database.get("title", [{"plain_text": "Unnamed"}])[0]["plain_text"]
        print(f"Title: {title}")
        print(f"ID: {database.get('id')}")
        
        # Print properties
        print("\n--- PROPERTIES ---")
        properties = database.get("properties", {})
        for name, prop in properties.items():
            prop_type = prop.get("type", "unknown")
            print(f"• {name} ({prop_type})")
            
            # For relations, show which database they connect to
            if prop_type == "relation":
                relation_db_id = prop.get("relation", {}).get("database_id", "unknown")
                print(f"  → Relates to database: {relation_db_id}")
        
        # Get a sample entry to see property values
        results = client.query_database(database_id, {}, None)
        if results:
            print("\n--- SAMPLE ENTRY ---")
            sample = results[0]
            print(f"Page ID: {sample.get('id')}")
            
            # Print property values
            print("Properties:")
            for name, prop in properties.items():
                prop_type = prop.get("type", "unknown")
                value = sample.get("properties", {}).get(name, {})
                
                if prop_type == "title" and "title" in value:
                    title_content = value.get("title", [])
                    title_text = title_content[0].get("plain_text", "") if title_content else ""
                    print(f"  • {name}: {title_text}")
                elif prop_type == "date" and "date" in value:
                    date_value = value.get("date", {})
                    start = date_value.get("start", "")
                    end = date_value.get("end", "")
                    date_str = start
                    if end:
                        date_str += f" to {end}"
                    print(f"  • {name}: {date_str}")
                elif prop_type == "select" and "select" in value:
                    select_value = value.get("select", {})
                    name = select_value.get("name", "") if select_value else ""
                    print(f"  • {name}: {name}")
                elif prop_type == "rich_text" and "rich_text" in value:
                    text_content = value.get("rich_text", [])
                    text = text_content[0].get("plain_text", "") if text_content else ""
                    if len(text) > 50:
                        text = text[:50] + "..."
                    print(f"  • {name}: {text}")
                elif prop_type == "relation" and "relation" in value:
                    relations = value.get("relation", [])
                    rel_ids = [rel.get("id", "") for rel in relations]
                    print(f"  • {name}: {len(rel_ids)} related items")
                else:
                    print(f"  • {name}: (value of type {prop_type})")
        
        # Try to find related databases
        print("\n--- RELATED DATABASES ---")
        for name, prop in properties.items():
            if prop.get("type") == "relation":
                relation_db_id = prop.get("relation", {}).get("database_id", "unknown")
                if relation_db_id != "unknown":
                    try:
                        rel_db = client.get_database(relation_db_id)
                        rel_title = rel_db.get("title", [{"plain_text": "Unnamed"}])[0]["plain_text"]
                        print(f"• {name} → {rel_title} ({relation_db_id})")
                    except Exception as e:
                        print(f"• {name} → Unable to access database ({relation_db_id}): {e}")
        
    except Exception as e:
        print(f"Error inspecting database: {e}")
        return False
    
    return True

def main():
    """Main function to run the script."""
    # Check if we have the necessary arguments
    if len(sys.argv) != 3:
        print("Usage: python view_notion_database.py <notion_token> <database_id>")
        print("Example: python view_notion_database.py secret_abc123 83452aab12345b12ab6576c99abab432")
        return 1
    
    token = sys.argv[1]
    database_id = sys.argv[2]
    
    print(f"Inspecting Notion database: {database_id}")
    inspect_database(token, database_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 