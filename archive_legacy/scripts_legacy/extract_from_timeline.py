#!/usr/bin/env python3
"""
Extract medical events from health timeline PDF.

This script extracts medical events from the health timeline PDF and writes them to
the medical_events.json file.
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
import subprocess
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("timeline_extract")

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF using pdftotext.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def parse_timeline_events(text: str) -> List[Dict[str, Any]]:
    """
    Parse timeline events from text.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        List of event dictionaries
    """
    events = []
    
    # Define patterns to extract year and events
    year_pattern = r'(\d{4})\s*(?::|$)'
    
    # Split text by lines
    lines = text.split('\n')
    
    current_year = None
    current_month = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check for year heading
        year_match = re.match(year_pattern, line)
        if year_match:
            current_year = year_match.group(1)
            continue
        
        # Check for month (assuming some consistent format)
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        month_found = False
        for idx, month in enumerate(months):
            if line.startswith(month) or line.lower().startswith(month.lower()):
                current_month = str(idx + 1).zfill(2)  # Convert to two-digit format
                month_found = True
                break
                
        if month_found:
            continue
            
        # If we have year and month, assume the line is an event
        if current_year and current_month:
            # Use the 15th as a default day if no specific day is found
            day = "15"
            
            # Try to extract day from the line
            day_match = re.search(r'(?:^|\s)(\d{1,2})(?:st|nd|rd|th)?[\s:]', line)
            if day_match:
                day = day_match.group(1).zfill(2)  # Ensure two digits
            
            # Create date in ISO format
            date = f"{current_year}-{current_month}-{day}"
            
            # Extract event details, skipping date part if present
            event_text = line
            if day_match:
                event_text = line[day_match.end():].strip()
                if event_text.startswith('-'):
                    event_text = event_text[1:].strip()
            
            # Skip empty events
            if not event_text:
                continue
                
            # Determine event type
            event_type = "medical_event"  # Default type
            
            # Check for appointment indicators
            if any(term in event_text.lower() for term in ["appointment", "visit", "consultation", "doctor", "physician", "specialist", "provider"]):
                event_type = "appointment"
            
            # Check for procedure indicators
            elif any(term in event_text.lower() for term in ["surgery", "procedure", "operation", "mri", "x-ray", "scan", "ultrasound", "imaging"]):
                event_type = "procedure"
                
            # Check for diagnosis indicators
            elif any(term in event_text.lower() for term in ["diagnosed", "diagnosis", "confirmed", "tested positive"]):
                event_type = "diagnosis"
                
            # Check for lab result indicators
            elif any(term in event_text.lower() for term in ["lab", "test result", "blood test", "blood work"]):
                event_type = "lab_result"
                
            # Create event object with standardized naming
            title = event_text
            
            # Apply standardized naming based on event type
            if event_type == "appointment":
                # Extract specialty from text
                specialties = [
                    "GP", "Cardiology", "Neurology", "Rheumatology", 
                    "Gastroenterology", "Dermatology", "Orthopedics",
                    "Gynecology", "Urology", "ENT", "Ophthalmology", 
                    "Psychiatry", "Psychology", "Physical Therapy"
                ]
                
                found_specialty = None
                for specialty in specialties:
                    if specialty.lower() in event_text.lower():
                        found_specialty = specialty
                        break
                        
                if found_specialty:
                    if found_specialty == "GP":
                        title = "GP appointment"
                    else:
                        title = f"{found_specialty} appointment"
                else:
                    title = "Medical appointment"
            
            elif event_type == "procedure":
                if "mri" in event_text.lower():
                    title = "MRI"
                elif "x-ray" in event_text.lower():
                    title = "X-ray"
                elif "ultrasound" in event_text.lower():
                    title = "Ultrasound"
                elif "ct" in event_text.lower() or "cat scan" in event_text.lower():
                    title = "CT Scan"
                else:
                    title = "Medical procedure"
            
            elif event_type == "lab_result":
                title = "Lab results"
            
            # Create the event
            event = {
                "date": date,
                "title": title,
                "description": event_text,
                "type": event_type,
                "source": "health_timeline"
            }
            
            events.append(event)
    
    return events

def save_events(events: List[Dict[str, Any]], output_file: Path) -> bool:
    """
    Save events to output file.
    
    Args:
        events: List of event dictionaries
        output_file: Path to output file
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(exist_ok=True)
        
        # Load existing events if file exists
        existing_events = []
        if output_file.exists():
            try:
                with open(output_file, 'r') as f:
                    existing_data = json.load(f)
                    if isinstance(existing_data, dict) and "events" in existing_data:
                        existing_events = existing_data["events"]
                    elif isinstance(existing_data, list):
                        existing_events = existing_data
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
        
        # Create output data with metadata
        output_data = {
            "metadata": {
                "updated": datetime.now().isoformat(),
                "source": "health_timeline",
                "event_count": len(combined_events)
            },
            "events": combined_events
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        logger.info(f"Saved {len(combined_events)} events to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving events to {output_file}: {e}")
        return False

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract medical events from timeline PDF")
    parser.add_argument("--output", type=str, help="Output file path", default="data/medical_events.json")
    args = parser.parse_args()
    
    output_file = Path(args.output)
    
    # Extract text from timeline PDF
    pdf_path = Path("input/pdf_documents/Entire_Health_Timeline_1080x1920_(1).pdf")
    
    if not pdf_path.exists():
        logger.error(f"Timeline PDF not found: {pdf_path}")
        return 1
    
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        logger.error("Failed to extract text from PDF")
        return 1
    
    logger.info(f"Extracted {len(text)} characters from PDF")
    
    # Parse events from text
    events = parse_timeline_events(text)
    
    if not events:
        logger.error("No events found in timeline")
        return 1
    
    logger.info(f"Extracted {len(events)} events from timeline")
    
    # Save events
    if save_events(events, output_file):
        logger.info(f"Successfully saved timeline events to {output_file}")
        return 0
    else:
        logger.error(f"Failed to save timeline events")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 