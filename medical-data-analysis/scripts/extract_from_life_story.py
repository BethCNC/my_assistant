#!/usr/bin/env python3
"""
Extract medical events from life story text file.

This script extracts medical events from the life story text file and writes them to
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
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.ai.entity_extraction import MedicalEntityExtractor
    from src.ai.text_analysis import MedicalTextAnalyzer
    ai_available = True
except ImportError:
    ai_available = False
    print("AI modules not available. Using basic extraction.")

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("life_story_extract")

def extract_events_from_text(text, use_ai=True):
    """Extract medical events from text."""
    events = []
    
    # Initialize AI models if available and requested
    entity_extractor = None
    text_analyzer = None
    
    if use_ai and ai_available:
        try:
            entity_extractor = MedicalEntityExtractor()
            text_analyzer = MedicalTextAnalyzer()
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            logger.warning("Continuing with rule-based extraction only")
    
    # Extract years and dates
    year_pattern = r'\b(19\d{2}|20\d{2})\b'
    years = re.findall(year_pattern, text)
    
    # Find paragraphs that mention years for context
    paragraphs = text.split('\n\n')
    
    # Store medical events by year
    year_events = {}
    
    # Use AI for entity extraction if available
    if use_ai and ai_available and entity_extractor:
        # Process text in chunks to avoid memory issues
        chunk_size = 2000  # Characters
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            
            try:
                # Extract medical entities using AI
                entities = entity_extractor.extract_entities(chunk)
                
                # Process medical conditions
                if "medical_conditions" in entities:
                    for condition in entities["medical_conditions"]:
                        # Try to find a year associated with this condition
                        condition_text = condition.get("text", "")
                        
                        # Look for years near the condition mention
                        year_matches = re.findall(year_pattern, chunk)
                        closest_year = None
                        
                        if year_matches:
                            # Use the nearest year as an approximation
                            closest_year = year_matches[0]
                            
                        # Create event
                        event = {
                            "name": f"Medical Condition: {condition.get('name', condition_text)}",
                            "date": f"{closest_year}-01-01" if closest_year else "Unknown",
                            "type": "Medical Condition",
                            "source_document": "beth life story.txt",
                            "description": condition_text,
                        }
                        
                        # Add confidence score if available
                        if "confidence" in condition:
                            event["confidence"] = condition["confidence"]
                            
                        events.append(event)
                
                # Process symptoms
                if "symptoms" in entities:
                    for symptom in entities["symptoms"]:
                        # Try to find a year associated with this symptom
                        symptom_text = symptom.get("text", "")
                        
                        # Look for years near the symptom mention
                        year_matches = re.findall(year_pattern, chunk)
                        closest_year = None
                        
                        if year_matches:
                            # Use the nearest year as an approximation
                            closest_year = year_matches[0]
                            
                        # Create event
                        event = {
                            "name": f"Symptom: {symptom.get('name', symptom_text)}",
                            "date": f"{closest_year}-01-01" if closest_year else "Unknown",
                            "type": "Symptom",
                            "source_document": "beth life story.txt",
                            "description": symptom_text,
                        }
                        
                        # Add confidence score if available
                        if "confidence" in symptom:
                            event["confidence"] = symptom["confidence"]
                            
                        events.append(event)
                
                # Process procedures
                if "procedures" in entities:
                    for procedure in entities["procedures"]:
                        # Try to find a year associated with this procedure
                        procedure_text = procedure.get("text", "")
                        
                        # Look for years near the procedure mention
                        year_matches = re.findall(year_pattern, chunk)
                        closest_year = None
                        
                        if year_matches:
                            # Use the nearest year as an approximation
                            closest_year = year_matches[0]
                            
                        # Create event
                        event = {
                            "name": f"Procedure: {procedure.get('name', procedure_text)}",
                            "date": f"{closest_year}-01-01" if closest_year else "Unknown",
                            "type": "Procedure",
                            "source_document": "beth life story.txt",
                            "description": procedure_text,
                        }
                        
                        # Add confidence score if available
                        if "confidence" in procedure:
                            event["confidence"] = procedure["confidence"]
                            
                        events.append(event)
                
            except Exception as e:
                logger.warning(f"Error in AI entity extraction: {str(e)}")
    
    # Rule-based extraction for specific medical events
    for paragraph in paragraphs:
        # Skip short paragraphs
        if len(paragraph) < 20:
            continue
            
        # Look for key medical phrases
        medical_keywords = [
            "diagnosed", "diagnosis", "medical", "doctor", "hospital", 
            "surgery", "pain", "symptom", "condition", "health",
            "spinal fusion", "bulimia", "anorexia", "autism", "adhd",
            "shoulder", "vomiting", "nausea", "staph infection"
        ]
        
        has_medical_content = any(keyword in paragraph.lower() for keyword in medical_keywords)
        
        if has_medical_content:
            # Look for dates/years in the paragraph
            year_matches = re.findall(year_pattern, paragraph)
            
            if year_matches:
                year = year_matches[0]  # Use the first year found
                
                # Create an event for this medical paragraph
                event_name = paragraph.split(".")[0][:50] + "..."  # Use first sentence for name
                
                event = {
                    "name": f"Life Story: {event_name}",
                    "date": f"{year}-01-01",  # Use January 1 as default date since only year is provided
                    "type": "Medical Event",
                    "purpose": "Life story medical event",
                    "source_document": "beth life story.txt",
                    "description": paragraph
                }
                
                events.append(event)
    
    # Remove duplicate events based on name and date
    unique_events = []
    seen = set()
    
    for event in events:
        key = (event.get("name", ""), event.get("date", ""))
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    return unique_events

def save_events(events, output_file):
    """Save events to the output file, merging with existing events if present."""
    try:
        # Load existing events if file exists
        existing_events = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, dict) and "events" in existing_data:
                    existing_events = existing_data["events"]
                elif isinstance(existing_data, list):
                    existing_events = existing_data
        
        # Merge events, avoiding duplicates
        unique_events = existing_events.copy()
        for event in events:
            # Skip if event is already present
            is_duplicate = False
            for existing in existing_events:
                if (event.get("name") == existing.get("name") and 
                    event.get("date") == existing.get("date") and
                    event.get("type") == existing.get("type")):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_events.append(event)
        
        # Sort by date
        unique_events.sort(key=lambda x: x.get("date", "9999-99-99"))
        
        # Write to output file
        with open(output_file, 'w') as f:
            json.dump({"events": unique_events}, f, indent=2)
        
        logger.info(f"Saved {len(unique_events)} events to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving events: {e}")
        return False

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract medical events from life story text")
    parser.add_argument("--output", type=str, help="Output file path", default="data/medical_events.json")
    args = parser.parse_args()
    
    # Set paths
    input_file = Path("input/text_documents/beth life story.txt")
    output_file = Path(args.output)
    
    # Ensure the text file exists
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return False
    
    # Ensure output directory exists
    output_file.parent.mkdir(exist_ok=True)
    
    # Read the text file
    logger.info(f"Reading text from {input_file}")
    try:
        with open(input_file, 'r') as f:
            text = f.read()
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        return False
    
    # Extract events from text
    logger.info("Extracting events from text")
    events = extract_events_from_text(text)
    
    logger.info(f"Extracted {len(events)} events from life story")
    
    # Save events to file
    if save_events(events, output_file):
        logger.info(f"Successfully saved events to {output_file}")
        return True
    else:
        logger.error("Failed to save events")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Script completed successfully")
    else:
        logger.error("Script failed")
        sys.exit(1) 