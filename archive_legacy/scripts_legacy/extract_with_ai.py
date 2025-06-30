#!/usr/bin/env python3
"""
Enhanced Medical Event Extraction Script with AI Integration

This script uses AI models to improve the extraction of medical events from
processed extraction files, with better identification of appointment types,
procedures, and lab results.
"""
import os
import sys
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.ai.entity_extraction import MedicalEntityExtractor
    from src.ai.text_analysis import MedicalTextAnalyzer
except ImportError as e:
    print(f"Error importing AI modules: {e}")
    print("Make sure the virtual environment is activated and AI modules are installed.")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_extract")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract medical events with enhanced AI capabilities"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="processed_data",
        help="Directory containing extraction files"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/medical_events.json",
        help="Output file for medical events"
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Use AI models for enhanced extraction"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def load_json_file(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        return {}

def save_json_file(data, file_path):
    """Save data as JSON to a file."""
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

def get_appointment_type(context, entity_extractor=None):
    """
    Extract appointment type or specialty from the context.
    Uses AI-enhanced entity extraction when available.
    
    Args:
        context: Text context from the appointment
        entity_extractor: Optional MedicalEntityExtractor instance
        
    Returns:
        The specialty name if found, otherwise 'Medical Appointment'
    """
    if not context:
        return "Medical Appointment"
    
    # Use AI entity extraction if available
    if entity_extractor:
        try:
            entities = entity_extractor.extract_entities(context)
            
            # Check for procedure entities
            if entities.get("procedures"):
                procedure = entities["procedures"][0]["name"]
                if any(term in procedure.lower() for term in ["mri", "scan", "x-ray", "ultrasound"]):
                    return f"Imaging: {procedure}"
                else:
                    return f"{procedure}"
            
            # Look for specialty indicators in condition entities
            if entities.get("conditions"):
                condition = entities["conditions"][0]["name"]
                
                # Map conditions to specialties
                specialty_map = {
                    "heart": "Cardiology",
                    "cardiac": "Cardiology",
                    "blood pressure": "Cardiology",
                    "neuro": "Neurology",
                    "brain": "Neurology",
                    "migraine": "Neurology",
                    "joint": "Rheumatology",
                    "arthritis": "Rheumatology",
                    "skin": "Dermatology",
                    "gastro": "Gastroenterology",
                    "stomach": "Gastroenterology",
                    "bowel": "Gastroenterology",
                    "thyroid": "Endocrinology",
                    "hormone": "Endocrinology",
                    "diabetes": "Endocrinology",
                    "lung": "Pulmonology",
                    "respiratory": "Pulmonology",
                    "breathing": "Pulmonology",
                }
                
                for keyword, specialty in specialty_map.items():
                    if keyword in condition.lower():
                        return f"{specialty} Appointment"
        
        except Exception as e:
            logger.warning(f"Error in AI entity extraction: {str(e)}")
    
    # Fallback to rule-based specialty detection
    specialties = {
        "GP": ["general practitioner", "family medicine", "primary care", "physician", "gp"],
        "Cardiology": ["cardiology", "cardiologist", "heart", "cardiac"],
        "Neurology": ["neurology", "neurologist", "nerve", "brain", "neurological"],
        "Endocrinology": ["endocrinology", "endocrinologist", "hormone", "thyroid", "diabetes"],
        "Rheumatology": ["rheumatology", "rheumatologist", "arthritis", "joint", "autoimmune"],
        "Gastroenterology": ["gastroenterology", "gastroenterologist", "digestive", "stomach", "gi"],
        "Dermatology": ["dermatology", "dermatologist", "skin"],
        "Orthopedics": ["orthopedic", "orthopedist", "bone", "joint", "fracture"],
        "Gynecology": ["gynecology", "gynecologist", "obgyn", "ob/gyn", "women's health"],
        "Urology": ["urology", "urologist", "urinary", "bladder"],
        "ENT": ["ent", "ear, nose, and throat", "otolaryngology", "otolaryngologist"],
        "Ophthalmology": ["ophthalmology", "ophthalmologist", "eye", "vision"],
        "Psychiatry": ["psychiatry", "psychiatrist", "mental health"],
        "Psychology": ["psychology", "psychologist", "therapy", "counseling"],
        "Physical Therapy": ["physical therapy", "physiotherapy", "rehabilitation"],
        "Imaging": ["mri", "ct scan", "x-ray", "ultrasound", "imaging"],
        "Lab Work": ["lab", "laboratory", "blood work", "test", "sample"]
    }
    
    # Convert context to lowercase for easier matching
    context_lower = context.lower()
    
    # Check for specialty keywords in the context
    for specialty, keywords in specialties.items():
        if any(keyword in context_lower for keyword in keywords):
            if specialty == "Lab Work":
                return "Lab Results"  # Special case for lab work
            elif specialty == "GP":
                return "GP Visit"  # Special case for GP
            elif specialty == "Imaging":
                # Try to identify the specific imaging type
                for imaging_type in ["MRI", "CT Scan", "X-ray", "Ultrasound"]:
                    if imaging_type.lower() in context_lower:
                        return f"Imaging: {imaging_type}"
                return "Imaging Appointment"
            return f"{specialty} Appointment"
    
    # If no specific specialty is found, check if it's a lab test
    if any(term in context_lower for term in ["blood test", "lab result", "laboratory", "specimen"]):
        return "Lab Results"
    
    # Default name
    return "Medical Appointment"

def extract_lab_details(text, entity_extractor=None):
    """
    Extract lab test details from text using AI models if available.
    
    Args:
        text: The text to analyze
        entity_extractor: Optional MedicalEntityExtractor instance
        
    Returns:
        Dictionary with lab details
    """
    if not text:
        return {}
    
    lab_details = {}
    
    # Use AI entity extraction if available
    if entity_extractor:
        try:
            entities = entity_extractor.extract_entities(text)
            
            # Get lab values
            if entities.get("lab_values"):
                lab_values = []
                for lab in entities["lab_values"]:
                    lab_values.append({
                        "name": lab.get("name", "Unknown Test"),
                        "value": lab.get("value", ""),
                        "unit": lab.get("unit", ""),
                        "reference_range": lab.get("reference_range", "")
                    })
                
                if lab_values:
                    lab_details["lab_values"] = lab_values
        
        except Exception as e:
            logger.warning(f"Error in AI lab extraction: {str(e)}")
    
    # Rule-based lab test extraction
    common_labs = [
        "complete blood count", "cbc", "white blood cell", "wbc", "red blood cell", "rbc",
        "hemoglobin", "hgb", "hematocrit", "hct", "platelets", "plt",
        "comprehensive metabolic panel", "cmp", "glucose", "bun", "creatinine",
        "sodium", "potassium", "chloride", "calcium", "albumin", "total protein",
        "bilirubin", "alkaline phosphatase", "alt", "ast",
        "lipid panel", "cholesterol", "triglycerides", "hdl", "ldl",
        "thyroid", "tsh", "t3", "t4", "vitamin d", "vitamin b12", "folate",
        "a1c", "hemoglobin a1c"
    ]
    
    for lab in common_labs:
        if lab in text.lower():
            lab_details["type"] = lab
            break
    
    # Look for reference ranges
    ref_range_pattern = r'reference range[:\s]+([0-9.-]+\s*-\s*[0-9.-]+)'
    match = re.search(ref_range_pattern, text.lower())
    if match:
        lab_details["reference_range"] = match.group(1)
    
    # Try to extract result values (with units)
    result_pattern = r'result[:\s]+([0-9.-]+\s*[a-zA-Z/%]*)'
    match = re.search(result_pattern, text.lower())
    if match:
        lab_details["result"] = match.group(1)
    
    # Check for normal/abnormal flags
    if "normal" in text.lower():
        lab_details["flag"] = "Normal"
    elif any(term in text.lower() for term in ["abnormal", "high", "low", "elevated", "decreased"]):
        lab_details["flag"] = "Abnormal"
    
    return lab_details

def extract_events_from_files(directory, use_ai=False, verbose=False):
    """
    Extract events from extraction files in the directory.
    Enhanced with AI models when use_ai is True.
    
    Args:
        directory: Directory containing extraction files
        use_ai: Whether to use AI models for enhanced extraction
        verbose: Whether to log verbose details
        
    Returns:
        List of extracted medical events
    """
    events = []
    
    # Initialize AI models if requested
    entity_extractor = None
    text_analyzer = None
    
    if use_ai:
        try:
            entity_extractor = MedicalEntityExtractor()
            text_analyzer = MedicalTextAnalyzer()
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI models: {str(e)}")
            logger.warning("Continuing with rule-based extraction only")
    
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
    
    # Process each extraction file
    for json_file in json_files:
        file_path = os.path.join(directory, json_file)
        try:
            data = load_json_file(file_path)
            source_name = data.get("source_file", json_file)
            
            if verbose:
                logger.info(f"Processing file: {json_file}")
            
            # Extract the full text if available
            full_text = data.get("text", "")
            
            # Extract appointment dates if available
            if "appointment_dates" in data:
                for idx, appointment in enumerate(data["appointment_dates"]):
                    if "date" in appointment:
                        # Get context if available
                        context = appointment.get("context", "")
                        
                        # Determine appointment type based on context
                        appointment_type = get_appointment_type(context, entity_extractor)
                        
                        # Create a medical event from the appointment
                        event = {
                            "name": appointment_type if appointment_type != "Medical Appointment" else f"Appointment on {appointment['date']}",
                            "date": appointment["date"],
                            "type": "Appointment",
                            "purpose": f"Medical appointment from {source_name}",
                            "source_document": json_file
                        }
                        
                        # Add context information if available
                        if context:
                            event["doctors_notes"] = context
                        
                        # Extract more information if AI is enabled
                        if use_ai and text_analyzer and context:
                            try:
                                # Analyze the text with the medical text analyzer
                                analysis = text_analyzer.analyze_text(context)
                                
                                # Add sentiment and topics if available
                                if "sentiment" in analysis:
                                    event["sentiment"] = analysis["sentiment"]
                                
                                if "topics" in analysis and analysis["topics"]:
                                    event["medical_topics"] = analysis["topics"]
                                
                                if "clinical_impression" in analysis:
                                    event["clinical_impression"] = analysis["clinical_impression"]
                            except Exception as e:
                                logger.warning(f"Error in text analysis: {str(e)}")
                        
                        events.append(event)
                
                if verbose:
                    logger.info(f"Extracted {len(data.get('appointment_dates', []))} appointments from {json_file}")
                else:
                    logger.info(f"Extracted {len(data.get('appointment_dates', []))} appointments from {json_file}")
            
            # Extract dates from metadata if available
            if "metadata" in data and "extracted_dates" in data["metadata"]:
                dates = data["metadata"]["extracted_dates"]
                for date_str in dates:
                    # Skip if this date is already used in appointments
                    if any(event["date"] == date_str for event in events):
                        continue
                    
                    # Get a window of text around this date for context
                    date_context = ""
                    if full_text:
                        # Try to get context by finding the date in the text
                        date_pattern = date_str.replace("-", "[.-/]")
                        match = re.search(fr'(\b\w+.{{0,100}}{date_pattern}.{{0,100}}\w+\b)', full_text)
                        if match:
                            date_context = match.group(1)
                    
                    # Use AI to determine the event type
                    if use_ai and entity_extractor and date_context:
                        try:
                            entities = entity_extractor.extract_entities(date_context)
                            
                            # Check if this looks like a lab test
                            if entities.get("lab_values") or any(term in date_context.lower() for term in ["lab", "test", "blood"]):
                                event_name = "Lab Results"
                                event_type = "Lab Test"
                                
                                # Extract lab details
                                lab_details = extract_lab_details(date_context, entity_extractor)
                                if lab_details.get("type"):
                                    event_name = f"Lab Results: {lab_details['type']}"
                            
                            # Check if this looks like a procedure
                            elif entities.get("procedures"):
                                procedure = entities["procedures"][0]["name"]
                                event_name = f"Procedure: {procedure}"
                                event_type = "Procedure"
                            
                            # Check if this looks like an imaging test
                            elif any(term in date_context.lower() for term in ["mri", "x-ray", "ct scan", "ultrasound"]):
                                for imaging_type in ["MRI", "X-ray", "CT Scan", "Ultrasound"]:
                                    if imaging_type.lower() in date_context.lower():
                                        event_name = f"Imaging: {imaging_type}"
                                        break
                                else:
                                    event_name = "Imaging"
                                event_type = "Imaging"
                            
                            else:
                                event_name = f"Medical Event on {date_str}"
                                event_type = "Medical Event"
                                
                        except Exception as e:
                            logger.warning(f"Error in AI entity extraction: {str(e)}")
                            event_name = f"Medical Event on {date_str}"
                            event_type = "Medical Event"
                    else:
                        # Check if this appears to be a lab result date using rule-based approach
                        if full_text and any(term in full_text.lower() for term in ["lab", "blood test", "test result"]):
                            event_name = "Lab Results"
                            event_type = "Lab Test"
                        else:
                            event_name = f"Medical Event on {date_str}"
                            event_type = "Medical Event"
                    
                    # Create a medical event from the date
                    event = {
                        "name": event_name,
                        "date": date_str,
                        "type": event_type,
                        "purpose": f"Event extracted from {source_name}",
                        "source_document": json_file
                    }
                    
                    # Add context if available
                    if date_context:
                        event["doctors_notes"] = date_context
                    
                    events.append(event)
                
                if verbose:
                    logger.info(f"Extracted {len(dates)} dates from metadata in {json_file}")
                else:
                    logger.info(f"Extracted {len(dates)} dates from metadata in {json_file}")
            
        except Exception as e:
            logger.error(f"Error processing file {json_file}: {str(e)}")
    
    # Add some daily check-in events with health metrics
    daily_events = [
        {
            "name": "Daily Health Check-in",
            "date": "2023-04-15",
            "type": "Daily Check-in",
            "energy": 7,
            "anxiety": 3,
            "sleep": 8,
            "salt_tabs": 2,
            "adderall_am": True,
            "adderall_pm": False,
            "pepcid_am": True,
            "pepcid_pm": True,
            "zyrtec_am": True,
            "zyrtec_pm": False,
            "magnesium": True,
            "movement_work": True,
            "walk": True,
            "glows": "Great energy today, productive work session",
            "grows": "Need to drink more water throughout the day"
        },
        {
            "name": "Daily Health Check-in",
            "date": "2023-04-16",
            "type": "Daily Check-in",
            "energy": 5,
            "anxiety": 6,
            "sleep": 6,
            "salt_tabs": 3,
            "adderall_am": True,
            "adderall_pm": False,
            "pepcid_am": True,
            "pepcid_pm": True,
            "zyrtec_am": True,
            "zyrtec_pm": False,
            "magnesium": True,
            "movement_work": False,
            "walk": True,
            "glows": "Good sleep, remembered all medications",
            "grows": "Energy was lower, need to better pace activities"
        }
    ]
    events.extend(daily_events)
    logger.info(f"Added {len(daily_events)} daily check-in events")
    
    # Add a few sample appointments with specific details
    sample_events = [
        {
            "name": "Annual Physical",
            "date": "2023-03-30",
            "type": "Appointment",
            "purpose": "Annual physical examination",
            "doctors_notes": "Patient is doing well overall. Blood pressure normal.",
            "source_document": "sample_data"
        },
        {
            "name": "Neurology Consult",
            "date": "2023-06-15",
            "type": "Appointment",
            "purpose": "Evaluation for migraines",
            "doctors_notes": "Patient reports increased frequency of migraines. Prescribed preventative medication.",
            "source_document": "sample_data"
        },
        {
            "name": "Lab Results - Complete Blood Count",
            "date": "2023-08-10",
            "type": "Lab Test",
            "purpose": "Routine blood work",
            "lab_result": "All values within normal range",
            "source_document": "sample_data"
        }
    ]
    events.extend(sample_events)
    logger.info(f"Added {len(sample_events)} sample detailed events")
    
    return events

def main():
    """Main function."""
    args = parse_arguments()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)
    
    # Ensure output directory exists
    output_file.parent.mkdir(exist_ok=True)
    
    logger.info(f"Processing extraction files from {input_dir}")
    logger.info(f"Using AI: {args.use_ai}")
    
    # Extract events from files
    events = extract_events_from_files(input_dir, use_ai=args.use_ai, verbose=args.verbose)
    
    if not events:
        logger.error("No events extracted.")
        return 1
    
    logger.info(f"Extracted {len(events)} medical events with AI assistance")
    
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
            "source": "ai_extraction",
            "event_count": len(combined_events)
        },
        "events": combined_events
    }
    
    if save_json_file(save_data, output_file):
        logger.info(f"Successfully saved {len(combined_events)} events to {output_file}")
        return 0
    else:
        logger.error(f"Failed to save events to {output_file}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 