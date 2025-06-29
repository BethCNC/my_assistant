#!/usr/bin/env python3
"""
Script to import processed medical records into Notion Medical Calendar database.

This script reads the JSON file created by import_2018_2019_records.py
and imports the records into the Notion Medical Calendar database.
"""

import os
import json
import datetime
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
INPUT_FILE = "data/notion_import_ready/notion_ready_entries.json"
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
MEDICAL_CALENDAR_DB_ID = "17b86edcae2c81c183e0e0a19a035932"
DOCTOR_DB_ID = "17b86edcae2c81558caafbb80647f6a9"

# Notion API endpoints
NOTION_API_BASE = "https://api.notion.com/v1"
PAGES_ENDPOINT = f"{NOTION_API_BASE}/pages"
DB_QUERY_ENDPOINT = f"{NOTION_API_BASE}/databases/{MEDICAL_CALENDAR_DB_ID}/query"
DOCTORS_QUERY_ENDPOINT = f"{NOTION_API_BASE}/databases/{DOCTOR_DB_ID}/query"

def get_notion_headers():
    """Get headers for Notion API requests."""
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY environment variable not set.")
    
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def get_doctor_id_by_name(doctor_name):
    """Get Notion doctor ID by doctor name."""
    # Extract last name from doctor name (e.g., "Dr. Smith" -> "Smith")
    last_name = doctor_name.split()[-1]
    
    # Query doctors database for matching doctor
    headers = get_notion_headers()
    payload = {
        "filter": {
            "property": "Name",
            "rich_text": {
                "contains": last_name
            }
        }
    }
    
    response = requests.post(DOCTORS_QUERY_ENDPOINT, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error querying doctors database: {response.text}")
        return None
    
    results = response.json().get("results", [])
    
    if not results:
        print(f"No doctor found with name containing '{last_name}'")
        return None
    
    return results[0]["id"]

def create_record_in_notion(entry):
    """Create a record in the Notion Medical Calendar database."""
    headers = get_notion_headers()
    
    # Parse date from string
    date_obj = datetime.datetime.fromisoformat(entry["date"])
    
    # Get doctor ID if available
    doctor_id = None
    if entry.get("doctor"):
        doctor_id = get_doctor_id_by_name(entry["doctor"])
    
    # Prepare properties for Notion
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": entry["title"]
                    }
                }
            ]
        },
        "Date": {
            "date": {
                "start": date_obj.isoformat()
            }
        },
        "Type": {
            "select": {
                "name": entry["type"]
            }
        }
    }
    
    # Add Doctor relation if available
    if doctor_id:
        properties["Doctor"] = {
            "relation": [
                {
                    "id": doctor_id
                }
            ]
        }
    
    # Create page in Notion
    payload = {
        "parent": {
            "database_id": MEDICAL_CALENDAR_DB_ID
        },
        "properties": properties,
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": entry["content"]
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    response = requests.post(PAGES_ENDPOINT, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error creating record: {response.text}")
        return False
    
    return True

def main():
    """Main function to import records into Notion."""
    print("Starting import of medical records into Notion...")
    
    # Check for Notion API key
    if not NOTION_API_KEY:
        print("Error: NOTION_API_KEY environment variable not set.")
        print("Set your Notion API key with: export NOTION_API_KEY=your_api_key")
        return
    
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found: {INPUT_FILE}")
        print("Run import_2018_2019_records.py first to generate this file.")
        return
    
    # Read input file
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        entries = json.load(infile)
    
    print(f"Found {len(entries)} records to import.")
    
    # Import each record into Notion
    success_count = 0
    for i, entry in enumerate(entries):
        print(f"Importing record {i+1}/{len(entries)}: {entry['title']}")
        if create_record_in_notion(entry):
            success_count += 1
    
    print(f"Import complete. Successfully imported {success_count}/{len(entries)} records.")

if __name__ == "__main__":
    main() 