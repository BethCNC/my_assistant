#!/usr/bin/env python3
"""
Create medical events from extraction files.

This script reads the extracted data from processed files and creates
a properly formatted medical_events.json file for the pipeline.
"""
import os
import sys
import json
import logging
import re
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the AI modules
try:
    from src.ai.text_analysis import MedicalTextAnalyzer
    text_analyzer = MedicalTextAnalyzer()
    ai_available = True
except ImportError:
    ai_available = False
    print("AI text analysis module not available. Using basic naming.")

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("create_events")

def load_json_file(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save JSON data to a file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {e}")
        return False

def format_date(date_string):
    """Format date string to ISO format (YYYY-MM-DD)."""
    # Try different date formats
    date_formats = [
        "%Y-%m-%d",  # 2023-01-15
        "%m/%d/%Y",  # 01/15/2023
        "%d/%m/%Y",  # 15/01/2023
        "%B %d, %Y", # January 15, 2023
        "%b %d, %Y", # Jan 15, 2023
        "%m-%d-%Y",  # 01-15-2023
        "%Y/%m/%d",  # 2023/01/15
    ]
    
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_string, date_format)
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return date_string  # Return as is if no format matches

def extract_medical_events(extraction_files: List[Path]) -> List[Dict[str, Any]]:
    """
    Extract medical events from a list of extraction files.
    """
    logger.info(f"Processing {len(extraction_files)} extraction files")
    all_events = []
    
    for file_path in extraction_files:
        logger.info(f"Processing file: {file_path}")
        
        extracted_data = load_json_file(file_path)
        
        if not extracted_data:
            continue
        
        # Process based on file type
        if "Atrium Patient Health Summary" in str(file_path):
            events = process_atrium_data(extracted_data, file_path)
            all_events.extend(events)
        elif "Novant" in str(file_path):
            events = process_novant_data(extracted_data, file_path)
            all_events.extend(events)
        else:
            # Generic processing for other file types
            events = process_general_medical_data(extracted_data, file_path)
            all_events.extend(events)
    
    return all_events

def process_atrium_data(data, file_path):
    """Process Atrium Health data to extract medical events."""
    events = []
    
    # Check for appointments
    if "Appointments" in data:
        appointments = data["Appointments"]
        if isinstance(appointments, list):
            for appointment in appointments:
                if "date" in appointment and "provider" in appointment:
                    event = {
                        "date": format_date(appointment["date"]),
                        "type": "appointment",
                        "source": os.path.basename(file_path),
                        "details": appointment
                    }
                    
                    # Use AI to determine appointment type if available
                    appointment_text = json.dumps(appointment)
                    if ai_available:
                        specialty = text_analyzer.identify_appointment_type(appointment_text)
                        event["title"] = specialty
                    else:
                        # Basic appointment naming
                        if "specialty" in appointment:
                            event["title"] = f"{appointment['specialty']} appointment"
                        else:
                            event["title"] = f"Medical appointment"
                    
                    events.append(event)
    
    # Check for labs
    if "Laboratory Results" in data and isinstance(data["Laboratory Results"], list):
        for lab in data["Laboratory Results"]:
            if "date" in lab:
                event = {
                    "date": format_date(lab["date"]),
                    "type": "lab_result",
                    "source": os.path.basename(file_path),
                    "details": lab
                }
                
                # Use AI to determine lab type if available
                lab_text = json.dumps(lab)
                if ai_available:
                    lab_type = text_analyzer.identify_lab_test_type(lab_text)
                    event["title"] = lab_type
                else:
                    # Basic lab naming as requested
                    event["title"] = "Lab results"
                
                events.append(event)
    
    # Check for procedures
    if "Procedures" in data and isinstance(data["Procedures"], list):
        for procedure in data["Procedures"]:
            if "date" in procedure:
                event = {
                    "date": format_date(procedure["date"]),
                    "type": "procedure",
                    "source": os.path.basename(file_path),
                    "details": procedure
                }
                
                # Use AI to determine procedure type if available
                procedure_text = json.dumps(procedure)
                if ai_available:
                    procedure_type = text_analyzer.identify_procedure_type(procedure_text)
                    event["title"] = procedure_type
                else:
                    # Basic procedure naming
                    if "name" in procedure:
                        procedure_name = procedure["name"]
                        if any(kw.lower() in procedure_name.lower() for kw in ["mri", "x-ray", "ct", "scan"]):
                            # Use the procedure name directly for imaging
                            event["title"] = procedure_name
                        else:
                            event["title"] = "Medical procedure"
                    else:
                        event["title"] = "Medical procedure"
                
                events.append(event)
    
    return events

def process_novant_data(data, file_path):
    """Process Novant Health data to extract medical events."""
    events = []
    
    # Check for visits
    if "Visits" in data and isinstance(data["Visits"], list):
        for visit in data["Visits"]:
            if "date" in visit:
                event = {
                    "date": format_date(visit["date"]),
                    "type": "appointment",
                    "source": os.path.basename(file_path),
                    "details": visit
                }
                
                # Use AI to determine appointment type if available
                visit_text = json.dumps(visit)
                if ai_available:
                    specialty = text_analyzer.identify_appointment_type(visit_text)
                    event["title"] = specialty
                else:
                    # Basic visit naming
                    if "department" in visit:
                        event["title"] = f"{visit['department']} appointment"
                    elif "provider" in visit:
                        event["title"] = "Medical appointment"
                    else:
                        event["title"] = "Medical appointment"
                
                events.append(event)
    
    # Check for labs
    if "Laboratory" in data and isinstance(data["Laboratory"], list):
        for lab in data["Laboratory"]:
            if "date" in lab:
                event = {
                    "date": format_date(lab["date"]),
                    "type": "lab_result",
                    "source": os.path.basename(file_path),
                    "details": lab
                }
                
                # Use AI to determine lab type if available
                lab_text = json.dumps(lab)
                if ai_available:
                    lab_type = text_analyzer.identify_lab_test_type(lab_text)
                    event["title"] = lab_type
                else:
                    # Basic lab naming
                    event["title"] = "Lab results"
                
                events.append(event)
    
    # Check for procedures
    if "Procedures" in data and isinstance(data["Procedures"], list):
        for procedure in data["Procedures"]:
            if "date" in procedure:
                event = {
                    "date": format_date(procedure["date"]),
                    "type": "procedure",
                    "source": os.path.basename(file_path),
                    "details": procedure
                }
                
                # Use AI to determine procedure type if available
                procedure_text = json.dumps(procedure)
                if ai_available:
                    procedure_type = text_analyzer.identify_procedure_type(procedure_text)
                    event["title"] = procedure_type
                else:
                    # Basic procedure naming
                    if "name" in procedure:
                        procedure_name = procedure["name"]
                        if any(kw.lower() in procedure_name.lower() for kw in ["mri", "x-ray", "ct", "scan"]):
                            # Use the procedure name directly for imaging
                            event["title"] = procedure_name
                        else:
                            event["title"] = "Medical procedure"
                    else:
                        event["title"] = "Medical procedure"
                
                events.append(event)
    
    return events

def process_general_medical_data(data, file_path):
    """Process general medical data to extract medical events."""
    events = []
    
    # Handle case where data might be a list of events
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "date" in item:
                # This appears to be an event already
                event = item.copy()
                event["source"] = os.path.basename(file_path)
                
                # Make sure it has a title
                if "title" not in event:
                    if "type" in event:
                        event_type = event["type"]
                        if event_type == "appointment":
                            event["title"] = "Medical Appointment"
                        elif event_type == "lab_result":
                            event["title"] = "Lab Results"
                        elif event_type == "procedure":
                            event["title"] = "Medical Procedure"
                        else:
                            event["title"] = "Medical Event"
                    else:
                        event["title"] = "Medical Event"
                
                # Use AI to improve event naming if available
                if ai_available:
                    event_text = json.dumps(event)
                    if "type" in event:
                        if event["type"] == "appointment":
                            specialty = text_analyzer.identify_appointment_type(event_text)
                            event["title"] = f"{specialty} Appointment"
                        elif event["type"] == "lab_result":
                            lab_type = text_analyzer.identify_lab_test_type(event_text)
                            event["title"] = f"{lab_type}"
                        elif event["type"] == "procedure":
                            procedure_type = text_analyzer.identify_procedure_type(event_text)
                            event["title"] = f"{procedure_type}"
                
                events.append(event)
                
    # Look for common sections in structured data
    elif isinstance(data, dict):
        # Check for medical events in various formats
        for key, value in data.items():
            # If the value is a list, check if it contains event-like items
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "date" in item:
                        event = {
                            "date": format_date(item["date"]),
                            "type": key.lower() if key.lower() in ["appointment", "lab_result", "procedure"] else "medical_event",
                            "source": os.path.basename(file_path),
                            "details": item
                        }
                        
                        # Determine event title
                        if "title" in item:
                            event["title"] = item["title"]
                        elif "name" in item:
                            event["title"] = item["name"]
                        else:
                            # Default title based on section key
                            event["title"] = f"{key.title()}"
                        
                        # Use AI to improve event naming if available
                        if ai_available:
                            event_text = json.dumps(item)
                            if event["type"] == "appointment":
                                specialty = text_analyzer.identify_appointment_type(event_text)
                                event["title"] = f"{specialty} Appointment"
                            elif event["type"] == "lab_result":
                                lab_type = text_analyzer.identify_lab_test_type(event_text)
                                event["title"] = f"{lab_type}"
                            elif event["type"] == "procedure":
                                procedure_type = text_analyzer.identify_procedure_type(event_text)
                                event["title"] = f"{procedure_type}"
                        
                        events.append(event)
    
    return events

def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create medical events from extraction files')
    parser.add_argument('--output', type=str, default='data/medical_events.json',
                        help='Output file path for medical events')
    args = parser.parse_args()
    
    # Set output path
    output_file = Path(args.output)
    
    # Ensure data directory exists
    output_file.parent.mkdir(exist_ok=True)
    
    # Get all extraction files
    extraction_files = list(Path("processed_data").glob("*_extraction.json"))
    
    if not extraction_files:
        logger.error("No extraction files found in processed_data directory")
        return False
    
    logger.info(f"Found {len(extraction_files)} extraction files")
    
    # Extract medical events
    events = extract_medical_events(extraction_files)
    
    if not events:
        logger.error("No events extracted")
        return False
    
    logger.info(f"Extracted {len(events)} medical events")
    
    # Check if output file exists and merge with existing events
    existing_events = []
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "events" in data:
                    existing_events = data["events"]
                elif isinstance(data, list):
                    existing_events = data
        except Exception as e:
            logger.error(f"Error loading existing events: {e}")
    
    # Combine events, removing duplicates
    seen_events = set()
    combined_events = []
    
    # Add existing events
    for event in existing_events:
        key = f"{event.get('title', '')}-{event.get('date', '')}-{event.get('type', '')}"
        seen_events.add(key)
        combined_events.append(event)
    
    # Add new events
    for event in events:
        key = f"{event.get('title', '')}-{event.get('date', '')}-{event.get('type', '')}"
        if key not in seen_events:
            seen_events.add(key)
            combined_events.append(event)
    
    # Sort events by date
    combined_events.sort(key=lambda x: x.get('date', '9999-99-99'))
    
    # Save events
    save_data = {
        "metadata": {
            "updated": datetime.now().isoformat(),
            "source": "extraction_files",
            "event_count": len(combined_events)
        },
        "events": combined_events
    }
    
    if save_json_file(save_data, output_file):
        logger.info(f"Successfully saved {len(combined_events)} events to {output_file}")
        return True
    else:
        logger.error(f"Failed to save events to {output_file}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Script completed successfully")
    else:
        logger.error("Script failed")
        sys.exit(1) 