#!/usr/bin/env python3
"""
Format medical events for Notion database import.

This script transforms the extracted medical events from JSON format into
a structure that can be imported directly into Notion databases.
"""
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.notion_integration.formatters import (
        format_title, format_rich_text, format_date,
        format_select, format_multi_select, format_relation,
        format_number, format_checkbox
    )
except ImportError:
    logging.error("Could not import Notion formatters. Make sure they exist in src/notion_integration/formatters.py")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notion_formatter")

def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure an argument parser."""
    parser = argparse.ArgumentParser(
        description="Format medical events for Notion database import"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="data/medical_events.json",
        help="Input file with extracted medical events (default: data/medical_events.json)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/notion_formatted_events.json",
        help="Output file for Notion-formatted events (default: data/notion_formatted_events.json)"
    )
    parser.add_argument(
        "--field-mapping",
        type=str,
        default="config/notion_field_mapping.json",
        help="Path to field mapping configuration (default: config/notion_field_mapping.json)"
    )
    return parser

def load_json_file(file_path: str) -> Dict:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data as a dictionary
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def save_json_file(data: Dict, file_path: str) -> bool:
    """
    Save data as JSON to a file.
    
    Args:
        data: Data to save
        file_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save data to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False

def determine_event_type(event: Dict[str, Any]) -> str:
    """
    Determine the Notion select value for event type.
    
    Args:
        event: Medical event data
        
    Returns:
        Standardized event type string
    """
    # If the event already has a type, use a standard mapping
    if "type" in event:
        event_type = event["type"].lower()
        
        if "appointment" in event_type:
            return "Appointment"
        elif "diagnosis" in event_type:
            return "Diagnosis"
        elif "lab" in event_type or "test" in event_type:
            return "Lab Test"
        elif "procedure" in event_type or "surgery" in event_type:
            return "Procedure"
        elif "imaging" in event_type or "mri" in event_type or "x-ray" in event_type:
            return "Imaging"
        elif "medication" in event_type:
            return "Medication"
        elif "symptom" in event_type:
            return "Symptom Report"
        elif "daily" in event_type:
            return "Daily Check-in"
        
    # Try to determine type from the event name
    name = event.get("name", "").lower()
    
    if "appointment" in name or "visit" in name or "consult" in name:
        return "Appointment"
    elif "diagnosed" in name or "diagnosis" in name:
        return "Diagnosis"
    elif "lab" in name or "test" in name:
        return "Lab Test"
    elif "procedure" in name or "surgery" in name:
        return "Procedure"
    elif "mri" in name or "x-ray" in name or "imaging" in name:
        return "Imaging"
    elif "medication" in name or "started" in name and "taking" in name:
        return "Medication"
    elif "symptom" in name:
        return "Symptom Report"
    
    # Default type if we can't determine
    return "Medical Event"

def format_event_for_notion(event: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Format a medical event for Notion import.
    
    Args:
        event: Medical event data
        field_mapping: Mapping from internal field names to Notion property names
        
    Returns:
        Notion-formatted properties for the event
    """
    properties = {}
    
    # Title (Name) field is required
    name = event.get("name", "Untitled Medical Event")
    properties[field_mapping["name"]] = format_title(name)
    
    # Date field
    if "date" in event and event["date"]:
        properties[field_mapping["date"]] = format_date(event["date"])
    
    # Event type
    event_type = determine_event_type(event)
    properties[field_mapping["type"]] = format_select(event_type)
    
    # Text fields
    for field in ["purpose", "personal_notes", "doctors_notes"]:
        if field in event and event[field] and field in field_mapping:
            properties[field_mapping[field]] = format_rich_text(str(event[field]))
    
    # Handle notes field specially - skip it as it's a relation field in Notion
    # if "notes" in event and event["notes"] and "notes" in field_mapping:
    #     properties[field_mapping["notes"]] = format_rich_text(str(event["notes"]))
    
    # Lab result (can be text or number)
    if "lab_result" in event and event["lab_result"] and "lab_result" in field_mapping:
        result = event["lab_result"]
        if isinstance(result, (int, float)):
            properties[field_mapping["lab_result"]] = format_number(result)
        else:
            properties[field_mapping["lab_result"]] = format_rich_text(str(result))
    
    # Numeric ratings (0-10 scale)
    for rating_field in ["energy", "anxiety", "shoulder_pain", "sleep", "salt_tabs"]:
        if rating_field in event and event[rating_field] is not None and rating_field in field_mapping:
            try:
                value = float(event[rating_field])
                properties[field_mapping[rating_field]] = format_number(value)
            except (ValueError, TypeError):
                pass
    
    # Boolean fields (checkboxes)
    for bool_field in ["adderall_am", "adderall_pm", "pepcid_am", "pepcid_pm", 
                      "zyrtec_am", "zyrtec_pm", "quercetin", "magnesium", "movement_work", "walk"]:
        if bool_field in event and bool_field in field_mapping:
            value = event[bool_field]
            if isinstance(value, bool):
                properties[field_mapping[bool_field]] = format_checkbox(value)
            elif isinstance(value, str):
                # Handle text "true"/"false" values
                properties[field_mapping[bool_field]] = format_checkbox(value.lower() == "true")
            elif isinstance(value, (int, float)):
                # Handle numeric 0/1 values
                properties[field_mapping[bool_field]] = format_checkbox(value > 0)
    
    # Rich text fields
    for text_field in ["glows", "grows"]:
        if text_field in event and event[text_field] and text_field in field_mapping:
            if isinstance(event[text_field], str):
                properties[field_mapping[text_field]] = format_rich_text(event[text_field])
            elif isinstance(event[text_field], list):
                # If it's a list, join it into a single string
                properties[field_mapping[text_field]] = format_rich_text(", ".join(event[text_field]))
    
    # Note: 'notes' field is a relation in Notion database, so we skip it here
    # as it should be handled by the relation creation process
    
    return properties

def format_events_for_notion(events: List[Dict[str, Any]], field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Format all medical events for Notion import.
    
    Args:
        events: List of medical events
        field_mapping: Mapping from internal field names to Notion property names
        
    Returns:
        List of Notion-formatted events
    """
    formatted_events = []
    
    for event in events:
        try:
            formatted_event = {
                "properties": format_event_for_notion(event, field_mapping),
                # Store the original event data for reference
                "original_data": event
            }
            
            formatted_events.append(formatted_event)
        except Exception as e:
            logger.error(f"Error formatting event: {str(e)}")
            logger.error(f"Problem event: {event}")
    
    return formatted_events

def main():
    """Main entry point for the script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Load medical events from input file
    data = load_json_file(args.input_file)
    
    if not data or "events" not in data:
        logger.error(f"No events found in input file: {args.input_file}")
        return 1
    
    events = data["events"]
    logger.info(f"Loaded {len(events)} medical events from {args.input_file}")
    
    # Load field mapping
    field_mapping = load_json_file(args.field_mapping)
    
    if not field_mapping or "medical_calendar" not in field_mapping:
        logger.error(f"Invalid field mapping in: {args.field_mapping}")
        return 1
    
    calendar_mapping = field_mapping["medical_calendar"]
    logger.info(f"Loaded field mapping with {len(calendar_mapping)} fields")
    
    # Format events for Notion
    formatted_events = format_events_for_notion(events, calendar_mapping)
    logger.info(f"Formatted {len(formatted_events)} events for Notion import")
    
    # Save formatted events to output file
    output_data = {
        "formatted_events": formatted_events,
        "metadata": {
            "formatting_date": datetime.now().isoformat(),
            "input_file": args.input_file,
            "event_count": len(formatted_events)
        }
    }
    
    if save_json_file(output_data, args.output_file):
        logger.info(f"Successfully saved {len(formatted_events)} formatted events to {args.output_file}")
        return 0
    else:
        logger.error(f"Failed to save formatted events to {args.output_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 