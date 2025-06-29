import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import requests
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notion_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
PROCESSED_DATA_DIR = Path('processed-data')
NOTION_API_BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Notion Database IDs
MEDICAL_CALENDAR_DB_ID = os.getenv("NOTION_MEDICAL_CALENDAR_ID")
SYMPTOMS_DB_ID = os.getenv("NOTION_SYMPTOMS_DB_ID")
MEDICAL_TEAM_DB_ID = os.getenv("NOTION_MEDICAL_TEAM_DB_ID")
MEDICATIONS_DB_ID = os.getenv("NOTION_MEDICATIONS_DB_ID")

def get_notion_headers():
    """Get headers for Notion API requests"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        raise ValueError("NOTION_API_KEY not found in environment variables")
    
    return {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

def load_processed_data():
    """Load the processed data from the JSON file"""
    notion_data_file = PROCESSED_DATA_DIR / "notion_import_data.json"
    if not notion_data_file.exists():
        logger.error(f"Notion import data file not found: {notion_data_file}")
        return None
    
    with open(notion_data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_notion_database(database_id, filter_property, value):
    """Search for an existing entry in a Notion database"""
    url = f"{NOTION_API_BASE_URL}/databases/{database_id}/query"
    
    # Create filter for the specific property
    data = {
        "filter": {
            "property": filter_property,
            "rich_text": {
                "equals": value
            }
        }
    }
    
    try:
        response = requests.post(url, headers=get_notion_headers(), json=data)
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[0]["id"] if results else None
    except Exception as e:
        logger.error(f"Error searching Notion database: {e}")
        return None

def create_rich_text_content(text):
    """Create a rich text content object for Notion properties"""
    if not text:
        return []
    
    return [
        {
            "type": "text",
            "text": {
                "content": str(text)
            }
        }
    ]

def create_relation_content(page_id):
    """Create a relation content object for Notion properties"""
    if not page_id:
        return []
    
    return [
        {
            "id": page_id
        }
    ]

def format_date(date_str):
    """Format date string for Notion date property"""
    if not date_str:
        return None
    
    try:
        # Handle ISO format
        parsed_date = datetime.fromisoformat(date_str)
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        # Try to use the string as is
        return date_str

def create_notion_page(database_id, properties):
    """Create a new page in a Notion database"""
    url = f"{NOTION_API_BASE_URL}/pages"
    
    data = {
        "parent": {
            "database_id": database_id
        },
        "properties": properties
    }
    
    try:
        response = requests.post(url, headers=get_notion_headers(), json=data)
        response.raise_for_status()
        page_id = response.json().get("id")
        logger.info(f"Created new page in database {database_id}: {page_id}")
        return page_id
    except Exception as e:
        logger.error(f"Error creating Notion page: {e}")
        return None

def import_medical_calendar(medical_calendar_entries):
    """Import medical calendar entries to Notion"""
    logger.info(f"Importing {len(medical_calendar_entries)} medical calendar entries")
    
    results = []
    for entry in medical_calendar_entries:
        # Check if entry already exists
        existing_id = search_notion_database(
            MEDICAL_CALENDAR_DB_ID, 
            "Title", 
            entry.get("title", "")
        )
        
        if existing_id:
            logger.info(f"Entry already exists: {entry.get('title')}")
            results.append({"id": existing_id, "title": entry.get("title")})
            continue
        
        # Format date property
        date_value = format_date(entry.get("date"))
        
        # Create properties object
        properties = {
            "Title": {
                "title": create_rich_text_content(entry.get("title"))
            },
            "Date": {
                "date": {
                    "start": date_value
                } if date_value else None
            },
            "Type": {
                "select": {
                    "name": entry.get("type", "Other")
                }
            },
            "Visit Summary/Lab Result": {
                "rich_text": create_rich_text_content(entry.get("summary"))
            }
        }
        
        # Add doctor/provider if available
        if entry.get("doctor"):
            # Try to find the provider in the medical team database
            provider_id = search_notion_database(
                MEDICAL_TEAM_DB_ID,
                "Name",
                entry.get("doctor")
            )
            
            if provider_id:
                properties["Doctor"] = {
                    "relation": create_relation_content(provider_id)
                }
        
        # Create the page
        page_id = create_notion_page(MEDICAL_CALENDAR_DB_ID, properties)
        if page_id:
            results.append({"id": page_id, "title": entry.get("title")})
        
        # Avoid rate limiting
        time.sleep(0.5)
    
    return results

def import_symptoms(symptoms_entries):
    """Import symptoms to Notion"""
    logger.info(f"Importing {len(symptoms_entries)} symptoms")
    
    results = []
    for entry in symptoms_entries:
        # Check if symptom already exists
        existing_id = search_notion_database(
            SYMPTOMS_DB_ID,
            "Name",
            entry.get("name", "")
        )
        
        if existing_id:
            logger.info(f"Symptom already exists: {entry.get('name')}")
            results.append({"id": existing_id, "name": entry.get("name")})
            continue
        
        # Format date property
        date_value = format_date(entry.get("date_recorded"))
        
        # Create properties object
        properties = {
            "Name": {
                "title": create_rich_text_content(entry.get("name"))
            },
            "First Occurrence": {
                "date": {
                    "start": date_value
                } if date_value else None
            },
            "Status": {
                "select": {
                    "name": "Active"  # Default to Active
                }
            },
            "Notes": {
                "rich_text": create_rich_text_content(f"Imported from {entry.get('source_file')}")
            }
        }
        
        # Create the page
        page_id = create_notion_page(SYMPTOMS_DB_ID, properties)
        if page_id:
            results.append({"id": page_id, "name": entry.get("name")})
        
        # Avoid rate limiting
        time.sleep(0.5)
    
    return results

def import_medical_team(medical_team_entries):
    """Import medical team to Notion"""
    logger.info(f"Importing {len(medical_team_entries)} medical team members")
    
    results = []
    for entry in medical_team_entries:
        # Check if provider already exists
        existing_id = search_notion_database(
            MEDICAL_TEAM_DB_ID,
            "Name",
            entry.get("name", "")
        )
        
        if existing_id:
            logger.info(f"Provider already exists: {entry.get('name')}")
            results.append({"id": existing_id, "name": entry.get("name")})
            continue
        
        # Format date property
        date_value = format_date(entry.get("first_visit"))
        
        # Create properties object
        properties = {
            "Name": {
                "title": create_rich_text_content(entry.get("name"))
            },
            "Specialty": {
                "select": {
                    "name": entry.get("specialty", "General Practitioner")
                }
            },
            "Facility/Clinic": {
                "rich_text": create_rich_text_content(entry.get("facility"))
            },
            "Date Care Began": {
                "date": {
                    "start": date_value
                } if date_value else None
            },
            "Notes": {
                "rich_text": create_rich_text_content(f"Imported from {entry.get('source_file')}")
            }
        }
        
        # Create the page
        page_id = create_notion_page(MEDICAL_TEAM_DB_ID, properties)
        if page_id:
            results.append({"id": page_id, "name": entry.get("name")})
        
        # Avoid rate limiting
        time.sleep(0.5)
    
    return results

def import_medications(medication_entries):
    """Import medications to Notion"""
    logger.info(f"Importing {len(medication_entries)} medications")
    
    results = []
    for entry in medication_entries:
        # Check if medication already exists with same name and dosage
        search_value = f"{entry.get('name')} {entry.get('dosage', '')}"
        existing_id = search_notion_database(
            MEDICATIONS_DB_ID,
            "Name",
            search_value.strip()
        )
        
        if existing_id:
            logger.info(f"Medication already exists: {search_value}")
            results.append({"id": existing_id, "name": search_value})
            continue
        
        # Format date property
        date_value = format_date(entry.get("prescribed_date"))
        
        # Create properties object
        properties = {
            "Name": {
                "title": create_rich_text_content(search_value.strip())
            },
            "Dosage": {
                "rich_text": create_rich_text_content(entry.get("dosage"))
            },
            "Start Date": {
                "date": {
                    "start": date_value
                } if date_value else None
            },
            "Status": {
                "select": {
                    "name": "Active"  # Default to Active
                }
            },
            "Notes": {
                "rich_text": create_rich_text_content(f"Imported from {entry.get('source_file')}")
            }
        }
        
        # Add prescriber if available
        if entry.get("prescribed_by"):
            # Try to find the provider in the medical team database
            provider_id = search_notion_database(
                MEDICAL_TEAM_DB_ID,
                "Name",
                entry.get("prescribed_by")
            )
            
            if provider_id:
                properties["Prescribed By"] = {
                    "relation": create_relation_content(provider_id)
                }
        
        # Create the page
        page_id = create_notion_page(MEDICATIONS_DB_ID, properties)
        if page_id:
            results.append({"id": page_id, "name": search_value})
        
        # Avoid rate limiting
        time.sleep(0.5)
    
    return results

def main():
    """Main function to import processed data to Notion"""
    logger.info("Starting Notion integration")
    
    # Check for Notion API key
    if not os.getenv("NOTION_API_KEY"):
        logger.error("NOTION_API_KEY not found. Please set it in .env file.")
        return
    
    # Check for database IDs
    if not all([MEDICAL_CALENDAR_DB_ID, SYMPTOMS_DB_ID, MEDICAL_TEAM_DB_ID, MEDICATIONS_DB_ID]):
        logger.error("One or more Notion database IDs not found. Please set them in .env file.")
        return
    
    # Load processed data
    notion_data = load_processed_data()
    if not notion_data:
        return
    
    # Import data to respective Notion databases
    results = {
        "medical_calendar": import_medical_calendar(notion_data.get("medical_calendar", [])),
        "symptoms": import_symptoms(notion_data.get("symptoms", [])),
        "medical_team": import_medical_team(notion_data.get("medical_team", [])),
        "medications": import_medications(notion_data.get("medications", []))
    }
    
    # Save import results
    results_file = PROCESSED_DATA_DIR / "notion_import_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Notion integration complete. Results saved to {results_file}")

if __name__ == "__main__":
    main() 