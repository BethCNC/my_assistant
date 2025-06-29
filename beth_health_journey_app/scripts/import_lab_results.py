#!/usr/bin/env python3
# Import Lab Results to Notion
# Script that processes parsed lab results and imports them into Notion

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time
from pathlib import Path
from dotenv import load_dotenv

# Try to import Notion SDK
try:
    from notion_client import Client
    HAVE_NOTION = True
except ImportError:
    HAVE_NOTION = False

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import our lab results parser
try:
    from scripts.lab_results_parser import parse_lab_results
    HAVE_LAB_PARSER = True
except ImportError:
    HAVE_LAB_PARSER = False


# Load environment variables from .env file
load_dotenv()

# Configure Notion API
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_CALENDAR_DB = os.getenv("NOTION_CALENDAR_DB_ID", "17b86edcae2c81c183e0e0a19a035932")
NOTION_SYMPTOMS_DB = os.getenv("NOTION_SYMPTOMS_DB_ID", "18a86edcae2c805a9ea1000c82df6d90")
NOTION_TEAM_DB = os.getenv("NOTION_TEAM_DB_ID", "17b86edcae2c81558caafbb80647f6a9")
NOTION_MEDICATIONS_DB = os.getenv("NOTION_MEDICATIONS_DB_ID", "17b86edcae2c81a7b28ae9fbcc7e7b62")
NOTION_NOTES_DB = os.getenv("NOTION_NOTES_DB_ID", "654e1ddc962f44698b1df6697375a321")


def check_dependencies() -> None:
    """Check if required dependencies are installed"""
    missing = []
    
    if not HAVE_NOTION:
        missing.append("notion_client")
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install required packages:")
        print("  pip install notion-client python-dotenv")
        sys.exit(1)


def create_notion_client() -> Any:
    """Create and configure Notion client"""
    if not HAVE_NOTION:
        raise ImportError("notion_client is not installed")
    
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY not found in environment variables. "
                       "Please set it in a .env file or environment.")
    
    client = Client(auth=NOTION_API_KEY)
    return client


def check_duplicate_lab_result(client: Any, test_name: str, date: str) -> Optional[str]:
    """
    Check if a lab result with similar name and date already exists in the Notion database
    
    Args:
        client: Notion client
        test_name: Name of the test
        date: Date of the test (in any format)
        
    Returns:
        Page ID of the duplicate if found, otherwise None
    """
    try:
        # Try to convert date to a standard format
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            try:
                # Try alternative formats
                for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%B %d, %Y", "%b %d, %Y"]:
                    try:
                        date_obj = datetime.strptime(date, fmt)
                        break
                    except ValueError:
                        continue
            except:
                # If all parsing fails, just use the string as is
                date_obj = None
        
        # Format date for filter if we successfully parsed it
        date_filter = None
        if date_obj:
            # Get the day before and the day after for the filter
            day_before = (date_obj.replace(hour=0, minute=0, second=0) - 
                         datetime.timedelta(days=1)).isoformat()
            day_after = (date_obj.replace(hour=23, minute=59, second=59) + 
                        datetime.timedelta(days=1)).isoformat()
            
            date_filter = {
                "date": {
                    "on_or_after": day_before,
                    "on_or_before": day_after
                }
            }
        
        # Query the database for similar entries
        query_params = {
            "database_id": NOTION_CALENDAR_DB,
            "filter": {
                "and": [
                    {
                        "property": "Type",
                        "select": {
                            "equals": "Lab Result"
                        }
                    }
                ]
            }
        }
        
        # Add date filter if we have one
        if date_filter:
            query_params["filter"]["and"].append({
                "property": "Date",
                **date_filter
            })
        
        # Execute the query
        response = client.databases.query(**query_params)
        
        # Check each result for a similar name
        for page in response.get("results", []):
            title = page.get("properties", {}).get("Name", {}).get("title", [])
            if title and any(test_name.lower() in block.get("plain_text", "").lower() for block in title):
                return page.get("id")
            
        return None
    
    except Exception as e:
        print(f"Error checking for duplicates: {e}")
        return None


def find_provider(client: Any, provider_name: str) -> Optional[str]:
    """
    Find a provider in the Notion Team database
    
    Args:
        client: Notion client
        provider_name: Name of the provider to find
        
    Returns:
        Page ID of the provider if found, otherwise None
    """
    if not provider_name:
        return None
    
    try:
        # Query the database for the provider
        response = client.databases.query(
            database_id=NOTION_TEAM_DB,
            filter={
                "property": "Name",
                "title": {
                    "contains": provider_name
                }
            }
        )
        
        # Return the first matching provider
        if response.get("results"):
            return response["results"][0]["id"]
        
        return None
    
    except Exception as e:
        print(f"Error finding provider: {e}")
        return None


def format_lab_content(lab_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format lab data into Notion blocks
    
    Args:
        lab_data: Parsed lab result data
        
    Returns:
        List of Notion block objects
    """
    blocks = []
    
    # Add header for lab result
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Lab Results"
                }
            }]
        }
    })
    
    # Add basic information
    basic_info = []
    
    # Test name
    if lab_data.get("test_name"):
        basic_info.append(f"**Test Name**: {lab_data['test_name']}")
    
    # Collection date
    if lab_data.get("collection_date"):
        basic_info.append(f"**Collection Date**: {lab_data['collection_date']}")
    
    # Report date
    if lab_data.get("report_date"):
        basic_info.append(f"**Report Date**: {lab_data['report_date']}")
    
    # Ordering provider
    if lab_data.get("ordering_provider"):
        basic_info.append(f"**Ordering Provider**: {lab_data['ordering_provider']}")
    
    # Performing lab
    if lab_data.get("performing_lab"):
        basic_info.append(f"**Performing Lab**: {lab_data['performing_lab']}")
    
    # Patient info
    if lab_data.get("patient_information"):
        patient_info = lab_data["patient_information"]
        if isinstance(patient_info, dict):
            # Format each item in patient info
            for key, value in patient_info.items():
                if value:
                    basic_info.append(f"**Patient {key.capitalize()}**: {value}")
        elif isinstance(patient_info, str):
            basic_info.append(f"**Patient Information**: {patient_info}")
    
    # Add basic info paragraph if we have any
    if basic_info:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": "\n".join(basic_info)
                    },
                    "annotations": {
                        "bold": False
                    }
                }]
            }
        })
    
    # Add results
    blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Test Results"
                }
            }]
        }
    })
    
    # Process results if we have them
    results = lab_data.get("results")
    abnormal_results = []
    
    if results and isinstance(results, list):
        # Create a bulleted list for each result
        for result in results:
            if not isinstance(result, dict):
                continue
                
            # Format the result line
            test_name = result.get("test_name", "Unknown test")
            value = result.get("result_value", result.get("value", ""))
            units = result.get("units", result.get("unit", ""))
            reference = result.get("reference_range", "")
            
            # Format the line with proper highlighting for abnormal results
            is_abnormal = result.get("is_abnormal", False) or result.get("flag", "") != ""
            
            # Build the text for this result
            result_text = f"{test_name}: {value}"
            if units:
                result_text += f" {units}"
            if reference:
                result_text += f" (Reference range: {reference})"
            if result.get("flag"):
                result_text += f" [{result['flag']}]"
            
            # Create the block
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": result_text
                        },
                        "annotations": {
                            "bold": is_abnormal,
                            "color": "red" if is_abnormal else "default"
                        }
                    }]
                }
            })
            
            # Track abnormal results for summary
            if is_abnormal:
                abnormal_results.append(f"{test_name}: {value} {units}")
    
    # Add notes and interpretations
    if "notes" in lab_data and lab_data["notes"]:
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": "Notes & Interpretation"
                    }
                }]
            }
        })
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": lab_data["notes"]
                    }
                }]
            }
        })
    
    # Return formatted blocks
    return blocks


def create_lab_result_in_notion(client: Any, lab_data: Dict[str, Any], 
                             file_path: Optional[str] = None) -> Optional[str]:
    """
    Create a new lab result entry in Notion
    
    Args:
        client: Notion client
        lab_data: Parsed lab result data
        file_path: Original file path (for reference)
        
    Returns:
        Page ID of the created entry
    """
    try:
        # Determine basic information about the lab result
        test_name = lab_data.get("test_name", "Lab Result")
        
        # Get date - try collection date first, then report date, then default to today
        result_date = None
        if lab_data.get("collection_date"):
            result_date = lab_data["collection_date"]
        elif lab_data.get("report_date"):
            result_date = lab_data["report_date"]
        else:
            result_date = datetime.now().strftime("%Y-%m-%d")
        
        # Format the date for the title
        try:
            date_obj = datetime.strptime(result_date, "%Y-%m-%d")
            date_display = date_obj.strftime("%b %d, %Y")
        except:
            date_display = result_date
        
        # Check for duplicates
        duplicate_id = check_duplicate_lab_result(client, test_name, result_date)
        if duplicate_id:
            print(f"  Found duplicate entry: {test_name} - {date_display}")
            
            # Update existing entry
            # Format content blocks
            blocks = format_lab_content(lab_data)
            
            # Append blocks to the existing page
            response = client.blocks.children.append(
                block_id=duplicate_id,
                children=blocks
            )
            
            print(f"  Updated existing entry with new information")
            return duplicate_id
        
        # Get provider relation if available
        provider_id = None
        if lab_data.get("ordering_provider"):
            provider_id = find_provider(client, lab_data["ordering_provider"])
            
        # Format page title
        page_title = f"{test_name} - {date_display}"
        
        # Create properties dictionary
        properties = {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": page_title
                        }
                    }
                ]
            },
            "Type": {
                "select": {
                    "name": "Lab Result"
                }
            }
        }
        
        # Add date property (if valid date)
        try:
            date_obj = datetime.strptime(result_date, "%Y-%m-%d")
            properties["Date"] = {
                "date": {
                    "start": date_obj.strftime("%Y-%m-%d")
                }
            }
        except:
            # If date parsing fails, just skip the date property
            pass
        
        # Add doctor property if we found a match
        if provider_id:
            properties["Doctor"] = {
                "relation": [
                    {
                        "id": provider_id
                    }
                ]
            }
        
        # Format abnormal results for summary
        abnormal_summary = ""
        results = lab_data.get("results", [])
        abnormal_results = []
        
        if results and isinstance(results, list):
            for result in results:
                if not isinstance(result, dict):
                    continue
                
                is_abnormal = result.get("is_abnormal", False) or result.get("flag", "") != ""
                if is_abnormal:
                    test_name = result.get("test_name", "Unknown test")
                    value = result.get("result_value", result.get("value", ""))
                    units = result.get("units", result.get("unit", ""))
                    abnormal_results.append(f"{test_name}: {value} {units}")
        
        if abnormal_results:
            abnormal_summary = "Abnormal results: " + ", ".join(abnormal_results)
            properties["Notes"] = {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": abnormal_summary
                        }
                    }
                ]
            }
        
        # Format content blocks
        blocks = format_lab_content(lab_data)
        
        # Create page
        response = client.pages.create(
            parent={
                "database_id": NOTION_CALENDAR_DB
            },
            properties=properties,
            children=blocks
        )
        
        page_id = response["id"]
        print(f"  Created new entry: {page_title} (ID: {page_id})")
        
        return page_id
        
    except Exception as e:
        print(f"Error creating lab result in Notion: {e}")
        return None


def process_lab_file(file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a single lab results file and import to Notion
    
    Args:
        file_path: Path to the lab results text or JSON file
        output_dir: Directory to save intermediate files
        
    Returns:
        Processed lab data
    """
    # Ensure file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    lab_data = None
    
    # Check if this is a JSON file with pre-parsed data
    if file_path.lower().endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                lab_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file: {e}")
                raise
    
    # If it's a text file, parse it
    elif file_path.lower().endswith('.txt') and HAVE_LAB_PARSER:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Parse the lab results text
        lab_data = parse_lab_results(text)
        
        # Save intermediate parsed results if output directory specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(file_path)
            json_filename = os.path.splitext(base_name)[0] + ".json"
            json_path = os.path.join(output_dir, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(lab_data, f, indent=2)
            
            print(f"  Saved parsed results to {json_path}")
    
    else:
        raise ValueError(f"Unsupported file type: {file_path}. Must be .json or .txt")
    
    # Import to Notion if we have valid data
    if lab_data:
        # Create Notion client
        client = create_notion_client()
        
        # Create the lab result in Notion
        create_lab_result_in_notion(client, lab_data, file_path)
    
    return lab_data


def process_directory(input_dir: str, output_dir: Optional[str] = None,
                     recursive: bool = False) -> List[Dict[str, Any]]:
    """
    Process all lab result files in a directory and import to Notion
    
    Args:
        input_dir: Directory containing lab results files
        output_dir: Directory to save intermediate files
        recursive: Whether to search subdirectories
        
    Returns:
        List of processed lab data
    """
    results = []
    
    # Get list of files to process
    if recursive:
        file_paths = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(('.txt', '.json')):
                    file_paths.append(os.path.join(root, file))
    else:
        file_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                    if os.path.isfile(os.path.join(input_dir, f)) and 
                      f.lower().endswith(('.txt', '.json'))]
    
    # Process each file
    for file_path in file_paths:
        try:
            print(f"Processing {os.path.basename(file_path)}...")
            result = process_lab_file(file_path, output_dir)
            results.append(result)
            # Small delay to avoid rate limiting
            time.sleep(1)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Processed {len(results)} files")
    return results


def main():
    """Main function to run when script is executed directly"""
    parser = argparse.ArgumentParser(
        description='Import lab results to Notion from parsed JSON or text files')
    parser.add_argument('input', help='Input file or directory to process (.json or .txt)')
    parser.add_argument('--output-dir', '-o', help='Directory to save intermediate files')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Recursively process directories')
    parser.add_argument('--no-import', '-n', action='store_true',
                       help='Only parse files, do not import to Notion')
    
    args = parser.parse_args()
    
    # Check if required dependencies are installed
    check_dependencies()
    
    input_path = args.input
    
    if os.path.isfile(input_path) and input_path.lower().endswith(('.txt', '.json')):
        # Process single file
        process_lab_file(input_path, args.output_dir)
    elif os.path.isdir(input_path):
        # Process directory
        process_directory(input_path, args.output_dir, args.recursive)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        print("Supported file types: .json, .txt")
        sys.exit(1)


if __name__ == "__main__":
    main() 