#!/usr/bin/env python3
"""
Extract medical data from processed files.

This script reads processed medical data files, extracts relevant medical events,
and outputs them in a structured format suitable for further processing.
"""
import os
import sys
import json
import argparse
import logging
import re
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_extraction")

def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure an argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract medical data from processed files"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="processed_data",
        help="Directory with processed medical data (default: processed_data)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/medical_events.json",
        help="Output file for extracted events (default: data/medical_events.json)"
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=0,
        help="Maximum number of events to extract (0 = no limit)"
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

def extract_date_from_filename(filename: str) -> Optional[str]:
    """
    Extract date from filename if present.
    
    Args:
        filename: Filename to process
        
    Returns:
        ISO formatted date string (YYYY-MM-DD) or None
    """
    # Look for date patterns in the filename (YYYY-MM-DD)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        return date_match.group(1)
    return None

def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date string to ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Normalized date string or None if invalid
    """
    if not date_str:
        return None
    
    # Handle already ISO formatted dates
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    # Try various date formats
    date_formats = [
        '%Y-%m-%d',      # 2023-01-15
        '%m/%d/%Y',      # 01/15/2023
        '%d/%m/%Y',      # 15/01/2023
        '%B %d, %Y',     # January 15, 2023
        '%b %d, %Y',     # Jan 15, 2023
        '%d %B %Y',      # 15 January 2023
        '%d %b %Y',      # 15 Jan 2023
        '%Y%m%d'         # 20230115
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    logger.warning(f"Couldn't normalize date: {date_str}")
    return None

def extract_data_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract medical events from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of extracted medical events
    """
    data = load_json_file(file_path)
    filename = os.path.basename(file_path)
    events = []
    
    # Extract file date if available
    file_date = extract_date_from_filename(filename)
    
    # Process extraction data
    if "extracted_data" in data:
        extracted_data = data["extracted_data"]
        
        # Extract medical events from the data
        if "medical_events" in extracted_data:
            for event in extracted_data["medical_events"]:
                # Clean and normalize event data
                event_data = {}
                
                # Basic fields
                if "name" in event:
                    event_data["name"] = event["name"]
                else:
                    # Use document title if event name not available
                    doc_title = data.get("document_metadata", {}).get("title")
                    if doc_title:
                        event_data["name"] = doc_title
                    else:
                        # Use filename as a last resort
                        event_data["name"] = os.path.splitext(filename)[0]
                
                # Get event date from event or file
                if "date" in event:
                    event_data["date"] = normalize_date(event["date"])
                elif file_date:
                    event_data["date"] = file_date
                
                # Additional fields if available
                for field in ["type", "doctor", "purpose", "notes"]:
                    if field in event:
                        event_data[field] = event[field]
                
                # Handle lists
                for list_field in ["related_diagnoses", "linked_symptoms", "medications"]:
                    if list_field in event:
                        event_data[list_field] = event[list_field]
                
                # Add source document info
                event_data["source_document"] = filename
                
                events.append(event_data)
        
        # Extract symptom data
        if "symptoms" in extracted_data:
            for symptom in extracted_data["symptoms"]:
                if "name" in symptom and "date" in symptom:
                    event_data = {
                        "name": f"Symptom: {symptom['name']}",
                        "date": normalize_date(symptom["date"]),
                        "type": "Symptom Report",
                        "linked_symptoms": [symptom["name"]],
                        "source_document": filename
                    }
                    
                    # Add severity if available
                    if "severity" in symptom:
                        event_data["severity"] = symptom["severity"]
                    
                    # Add notes if available
                    if "notes" in symptom:
                        event_data["notes"] = symptom["notes"]
                    
                    events.append(event_data)
    
    return events

def extract_medical_events_from_directory(directory: str, max_events: int = 0) -> List[Dict[str, Any]]:
    """
    Extract medical events from all JSON files in a directory.
    
    Args:
        directory: Directory containing extracted medical data
        max_events: Maximum number of events to extract (0 = no limit)
        
    Returns:
        List of medical events
    """
    events = []
    
    # Check if directory exists
    if not os.path.isdir(directory):
        logger.error(f"Directory not found: {directory}")
        return events
    
    # Get all JSON files with _extraction.json suffix
    json_files = [f for f in os.listdir(directory) if f.endswith('_extraction.json')]
    
    if not json_files:
        logger.warning(f"No _extraction.json files found in {directory}")
        return events
    
    logger.info(f"Found {len(json_files)} extraction files in {directory}")
    
    for json_file in json_files:
        file_path = os.path.join(directory, json_file)
        
        try:
            # Extract events from file
            file_events = extract_data_from_json(file_path)
            events.extend(file_events)
            
            logger.info(f"Extracted {len(file_events)} events from {json_file}")
            
            # Stop if we've reached max events
            if max_events > 0 and len(events) >= max_events:
                events = events[:max_events]
                logger.info(f"Reached maximum events limit ({max_events})")
                break
                
        except Exception as e:
            logger.error(f"Error processing file {json_file}: {str(e)}")
    
    return events

def main():
    """Main entry point for the script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Extract medical events from directory
    logger.info(f"Extracting medical events from {args.input_dir}")
    events = extract_medical_events_from_directory(args.input_dir, args.max_events)
    
    if not events:
        logger.warning("No medical events extracted")
        return 1
    
    logger.info(f"Extracted {len(events)} medical events")
    
    # Save extracted events to output file
    output_data = {
        "events": events,
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "source_directory": args.input_dir,
            "event_count": len(events)
        }
    }
    
    if save_json_file(output_data, args.output_file):
        logger.info(f"Successfully saved {len(events)} events to {args.output_file}")
        return 0
    else:
        logger.error(f"Failed to save events to {args.output_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 