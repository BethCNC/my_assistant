#!/usr/bin/env python3
"""
Notion Medical Import Script

This script processes extracted medical text files and imports them into the
Notion Medical Calendar database, organizing them by date, provider, and type.
"""

import os
import re
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests
from dateutil import parser
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("notion_import.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_MEDICAL_CALENDAR_DB = "17b86edcae2c81c183e0e0a19a035932"  # Medical Calendar DB ID
NOTION_DOCTOR_DB = "17b86edcae2c81558caafbb80647f6a9"  # Medical Team DB ID

EXTRACTED_TEXT_DIR = Path("data/extracted_text")
OUTPUT_DIR = Path("data/notion_import_ready")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Record type mapping based on file content
RECORD_TYPE_PATTERNS = {
    r"(?i)lab\s*results?|test\s*results?": "Lab Result",
    r"(?i)imaging|mammogram|x-ray|mri|ct|ultrasound": "Imaging",
    r"(?i)follow\s*up|follow-up": "Follow-up",
    r"(?i)initial\s*consult|initial\s*visit|new\s*patient": "Initial Consult",
    r"(?i)surgery|surgical|procedure": "Surgery",
    r"(?i)therapy|physical\s*therapy|occupational\s*therapy": "Therapy",
    r"(?i)emergency|urgent\s*care|er\s*visit": "Emergency/Urgent Care",
}

# Doctor specialty mapping based on keywords
SPECIALTY_MAPPING = {
    r"(?i)rheumat": "Rheumatology",
    r"(?i)endo": "Endocrinology",
    r"(?i)gp|primary\s*care|family\s*medicine": "General Practice",
    r"(?i)gi|gastro": "Gastroenterology",
    r"(?i)ortho": "Orthopedics",
    r"(?i)neuro": "Neurology",
    r"(?i)psych": "Psychiatry",
    r"(?i)gyn": "Gynecology",
    r"(?i)derm": "Dermatology",
    r"(?i)cardio": "Cardiology",
    r"(?i)pulm": "Pulmonology",
}

def get_notion_headers():
    """Return headers for Notion API requests."""
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def extract_date(text):
    """Extract the date from the medical record text."""
    # Common birthdate pattern to avoid - especially 09/13/1982
    birthdate_indicators = ["DOB", "Date of birth", "Birth date"]
    
    # First look for specific service date patterns - highest priority
    service_date_patterns = [
        r'(?:Date of Service|DOS|Visit Date|Encounter Date|Report Date|Collection Date)[\s:]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'(?:Date of Service|DOS|Visit Date|Encounter Date|Report Date|Collection Date)[\s:]+(\w+\s+\d{1,2},?\s+\d{4})'
    ]
    
    for pattern in service_date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1)
            try:
                # Try to parse the date
                if re.match(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}', date_str):
                    # Format: MM/DD/YYYY or similar
                    parts = re.split(r'[\/\-\.]', date_str)
                    if len(parts) == 3:
                        month, day, year = parts
                        # Handle 2-digit years
                        if len(year) == 2:
                            year = '20' + year if int(year) < 50 else '19' + year
                        
                        date = datetime.datetime(int(year), int(month), int(day))
                        
                        # Validate reasonable date range (2010-2025)
                        if 2010 <= date.year <= 2025:
                            logger.info(f"Found service date: {date}")
                            return date
                else:
                    # Format: Month DD, YYYY
                    date = parse_text_date(date_str)
                    if date and 2010 <= date.year <= 2025:
                        logger.info(f"Found service date: {date}")
                        return date
            except (ValueError, IndexError) as e:
                continue
    
    # Next, find all dates in the text and filter out birthdates
    date_patterns = [
        r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\w+\s+\d{1,2},?\s+\d{4})'  # Month DD, YYYY
    ]
    
    candidate_dates = []
    
    # Check numeric dates (MM/DD/YYYY)
    matches = re.finditer(date_patterns[0], text)
    for match in matches:
        # Check if this date is near a birthdate indicator
        start_pos = max(0, match.start() - 20)
        end_pos = min(len(text), match.end() + 5)
        context = text[start_pos:end_pos].upper()
        
        # Skip if this appears to be a birthdate
        if any(indicator.upper() in context for indicator in birthdate_indicators):
            continue
            
        try:
            month, day, year = match.groups()
            
            # Handle 2-digit years
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year
                
            date = datetime.datetime(int(year), int(month), int(day))
            
            # Validate reasonable date range
            if 2010 <= date.year <= 2025:
                candidate_dates.append(date)
        except (ValueError, IndexError):
            # Try alternative format (day and month reversed)
            try:
                day, month, year = match.groups()
                
                # Handle 2-digit years
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                    
                date = datetime.datetime(int(year), int(month), int(day))
                
                # Validate reasonable date range
                if 2010 <= date.year <= 2025:
                    candidate_dates.append(date)
            except (ValueError, IndexError):
                continue
    
    # Check text dates (Month DD, YYYY)
    matches = re.finditer(date_patterns[1], text)
    for match in matches:
        # Check if this date is near a birthdate indicator
        start_pos = max(0, match.start() - 20)
        end_pos = min(len(text), match.end() + 5)
        context = text[start_pos:end_pos].upper()
        
        # Skip if this appears to be a birthdate
        if any(indicator.upper() in context for indicator in birthdate_indicators):
            continue
            
        try:
            date = parse_text_date(match.group(1))
            if date and 2010 <= date.year <= 2025:
                candidate_dates.append(date)
        except (ValueError, IndexError):
            continue
    
    # Return the most recent valid date found, or None if no valid dates
    if candidate_dates:
        # Sort by recency (newest first)
        sorted_dates = sorted(candidate_dates, reverse=True)
        most_recent = sorted_dates[0]
        
        # Verify this isn't a birthdate by checking the specific date
        if most_recent.month == 9 and most_recent.day == 13 and most_recent.year == 1982:
            logger.warning("Suspected birthdate found, skipping")
            return None if len(sorted_dates) == 1 else sorted_dates[1]
            
        return most_recent
    
    return None

def parse_text_date(date_str):
    """Parse a textual date like 'January 2, 2020'."""
    try:
        return datetime.datetime.strptime(date_str, "%B %d, %Y")
    except ValueError:
        try:
            return datetime.datetime.strptime(date_str, "%B %d %Y")
        except ValueError:
            try:
                return datetime.datetime.strptime(date_str, "%b %d, %Y")
            except ValueError:
                try:
                    return datetime.datetime.strptime(date_str, "%b %d %Y")
                except ValueError:
                    return None

def extract_doctor(text):
    """Extract doctor name and specialty from the text."""
    doctor_info = {"name": None, "specialty": None}
    
    # Common patterns for doctor names
    doctor_patterns = [
        r'(?:Dr\.|Doctor)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'(?:Physician|Provider|Attending):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*(?:MD|DO|NP|PA)'
    ]
    
    for pattern in doctor_patterns:
        matches = re.search(pattern, text)
        if matches:
            doctor_info["name"] = matches.group(1)
            break
    
    # Extract specialty based on keywords
    for pattern, specialty in SPECIALTY_MAPPING.items():
        if re.search(pattern, text):
            doctor_info["specialty"] = specialty
            break
    
    return doctor_info

def determine_record_type(filename, text):
    """Determine the type of medical record based on content analysis."""
    # First check the filename for clues
    filename_lower = filename.lower()
    
    if "lab" in filename_lower or "test" in filename_lower:
        return "Lab Result"
    elif "imaging" in filename_lower or "mammogram" in filename_lower:
        return "Imaging"
    elif "surgery" in filename_lower or "procedure" in filename_lower:
        return "Surgery"
    
    # Then check the content for patterns
    for pattern, record_type in RECORD_TYPE_PATTERNS.items():
        if re.search(pattern, text):
            return record_type
    
    # Default to Doctor's Notes if type can't be determined
    return "Doctor's Notes - Appt Notes"

def extract_diagnoses(text):
    """Extract diagnoses mentioned in the text."""
    diagnoses = []
    
    # Common patterns for diagnoses sections
    diagnosis_sections = [
        r'(?:Diagnosis|Assessment|Impression|Problem List):(.*?)(?:\n\n|\n[A-Z])',
        r'(?:Diagnosed with|Diagnoses include):(.*?)(?:\n\n|\n[A-Z])'
    ]
    
    # Common chronic conditions to look for
    conditions = [
        "Psoriatic Arthritis", "PsA", 
        "Graves Disease", "Hyperthyroidism",
        "Bipolar Disorder", "PTSD", "ADHD",
        "Anorexia", "Eating Disorder",
        "Ehlers-Danlos Syndrome", "EDS",
        "Fibromyalgia"
    ]
    
    # First try to find a diagnosis section
    for pattern in diagnosis_sections:
        section_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if section_match:
            diagnosis_text = section_match.group(1)
            # Split by common delimiters and clean up
            for item in re.split(r'[,;.\n]', diagnosis_text):
                item = item.strip()
                if item and len(item) > 3:  # Avoid very short items
                    diagnoses.append(item)
    
    # If no diagnoses found in sections, look for known conditions
    if not diagnoses:
        for condition in conditions:
            if re.search(r'\b' + re.escape(condition) + r'\b', text, re.IGNORECASE):
                diagnoses.append(condition)
    
    return diagnoses

def extract_symptoms(text):
    """Extract symptoms mentioned in the text."""
    symptoms = []
    
    # Common patterns for symptoms sections
    symptom_sections = [
        r'(?:Symptoms|Chief Complaint|CC|Subjective):(.*?)(?:\n\n|\n[A-Z])',
        r'(?:Patient reports|Patient complains of|Patient presents with):(.*?)(?:\n\n|\n[A-Z])'
    ]
    
    # Common symptoms to look for
    common_symptoms = [
        "pain", "fatigue", "stiffness", "swelling", "rash", 
        "weakness", "numbness", "dizziness", "nausea",
        "headache", "fever", "chills", "cough"
    ]
    
    # First try to find a symptoms section
    for pattern in symptom_sections:
        section_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if section_match:
            symptom_text = section_match.group(1)
            # Look for symptom phrases
            for symptom in common_symptoms:
                symptom_pattern = fr'\b{symptom}\b\s+(?:in|of|at)?\s+(?:the)?\s+([a-z\s]+)'
                for match in re.finditer(symptom_pattern, symptom_text, re.IGNORECASE):
                    if match:
                        full_symptom = f"{symptom} in {match.group(1)}".strip()
                        symptoms.append(full_symptom)
    
    # If no structured symptoms found, look for common symptom mentions
    if not symptoms:
        for symptom in common_symptoms:
            symptom_pattern = fr'\b{symptom}\b\s+(?:in|of|at)?\s+(?:the)?\s+([a-z\s]+)'
            for match in re.finditer(symptom_pattern, text, re.IGNORECASE):
                if match:
                    full_symptom = f"{symptom} in {match.group(1)}".strip()
                    symptoms.append(full_symptom)
    
    return symptoms

def extract_medications(text):
    """Extract medications mentioned in the text."""
    medications = []
    
    # Look for a medications section
    med_section_pattern = r'(?:Medications|Current Medications|Active Medications|Medication List):(.*?)(?:\n\n|\n[A-Z])'
    
    # Common medications to look for
    common_meds = [
        "Methotrexate", "Humira", "Prednisone", "Adderall", 
        "Zoloft", "Zyrtec", "Claritin", "folic acid"
    ]
    
    # First try to find a medications section
    section_match = re.search(med_section_pattern, text, re.DOTALL | re.IGNORECASE)
    if section_match:
        med_text = section_match.group(1)
        # Look for medication names followed by dosage information
        med_pattern = r'([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml))'
        for match in re.finditer(med_pattern, med_text, re.IGNORECASE):
            if match:
                med_name = match.group(1).strip()
                med_dosage = match.group(2).strip()
                medications.append(f"{med_name} {med_dosage}")
    
    # If no structured medications found, look for common medication mentions
    if not medications:
        for med in common_meds:
            if re.search(r'\b' + re.escape(med) + r'\b', text, re.IGNORECASE):
                # Try to find dosage near the medication name
                med_pattern = fr'\b{re.escape(med)}\b\s+(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml))'
                dosage_match = re.search(med_pattern, text, re.IGNORECASE)
                
                if dosage_match:
                    medications.append(f"{med} {dosage_match.group(1)}")
                else:
                    medications.append(med)
    
    return medications

def create_notion_entry(filename, record_data):
    """Create a structured entry for Notion import."""
    
    # Extract needed fields
    date = record_data.get("date")
    if date is None:
        # Default to today if date couldn't be extracted
        date = datetime.datetime.now()
    
    formatted_date = date.strftime("%Y-%m-%d")
    
    doctor_info = record_data.get("doctor", {})
    doctor_name = doctor_info.get("name", "Unknown")
    
    record_type = record_data.get("type", "Doctor's Notes - Appt Notes")
    diagnoses = record_data.get("diagnoses", [])
    symptoms = record_data.get("symptoms", [])
    medications = record_data.get("medications", [])
    
    # Format the title based on the record type
    if record_type == "Lab Result":
        # Extract test type for lab results
        test_type = "Blood Work"  # Default
        if "thyroid" in filename.lower():
            test_type = "Thyroid Panel"
        elif "cbc" in filename.lower():
            test_type = "CBC"
        elif "comprehensive" in filename.lower():
            test_type = "Comprehensive Panel"
        
        title = f"{test_type} - {date.strftime('%b %d %Y')}"
    elif record_type == "Imaging":
        # Extract imaging type
        imaging_type = "Scan"  # Default
        if "mammogram" in filename.lower():
            imaging_type = "Mammogram"
        elif "mri" in filename.lower():
            imaging_type = "MRI"
        elif "xray" in filename.lower() or "x-ray" in filename.lower():
            imaging_type = "X-Ray"
        
        title = f"{imaging_type} - {date.strftime('%b %d %Y')}"
    else:
        # For appointments, use the specialty if available
        specialty = doctor_info.get("specialty", "Medical")
        title = f"{specialty} Visit - {date.strftime('%b %d %Y')}"
    
    # Create the Notion entry properties
    entry = {
        "title": title,
        "date": formatted_date,
        "type": record_type,
        "doctor": doctor_name,
        "diagnoses": diagnoses,
        "symptoms": symptoms,
        "medications": medications,
        "source_file": filename,
        "content": record_data.get("content", "")
    }
    
    return entry

def find_doctor_in_notion(doctor_name):
    """Find a doctor in the Notion Medical Team database."""
    if not NOTION_API_KEY:
        logger.warning("NOTION_API_KEY not found. Unable to search for doctor.")
        return None
    
    try:
        response = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_DOCTOR_DB}/query",
            headers=get_notion_headers(),
            json={
                "filter": {
                    "property": "Name",
                    "title": {
                        "contains": doctor_name
                    }
                }
            }
        )
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                # Return the ID of the first matching doctor
                return results[0]["id"]
    except Exception as e:
        logger.error(f"Error searching for doctor: {e}")
    
    return None

def add_to_notion_medical_calendar(entry):
    """Add an entry to the Notion Medical Calendar database."""
    if not NOTION_API_KEY:
        logger.warning("NOTION_API_KEY not found. Unable to add to Notion.")
        return False
    
    try:
        # Format the properties for Notion
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
                    "start": entry["date"]
                }
            },
            "Type": {
                "select": {
                    "name": entry["type"]
                }
            }
        }
        
        # Add doctor relation if we have one
        doctor_id = find_doctor_in_notion(entry["doctor"])
        if doctor_id:
            properties["Doctor"] = {
                "relation": [
                    {
                        "id": doctor_id
                    }
                ]
            }
        
        # Create the page in Notion
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=get_notion_headers(),
            json={
                "parent": {
                    "database_id": NOTION_MEDICAL_CALENDAR_DB
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
                                        "content": entry["content"][:2000] if entry["content"] else "No content extracted."
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully added '{entry['title']}' to Notion")
            return True
        else:
            logger.error(f"Failed to add to Notion: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error adding to Notion: {e}")
        return False

def process_file(filepath):
    """Process a single medical record file."""
    filename = os.path.basename(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # First, try to get date from filename if it contains date info
        filename_date = None
        date_pattern = r'(\d{1,2})[_\-\.](\d{1,2})[_\-\.](\d{2,4})'
        
        # Try to extract date from filename first
        match = re.search(date_pattern, filename)
        if match:
            month, day, year = match.groups()
            # Handle 2-digit years
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year
                
            try:
                filename_date = datetime.datetime(int(year), int(month), int(day))
                # Validate reasonable date range
                if not (2010 <= filename_date.year <= 2025):
                    filename_date = None
            except ValueError:
                # Try reversing month/day in case of alternative format
                try:
                    filename_date = datetime.datetime(int(year), int(day), int(month))
                    if not (2010 <= filename_date.year <= 2025):
                        filename_date = None
                except ValueError:
                    filename_date = None
        
        # If filename couldn't provide date, try content
        content_date = extract_date(text)
        
        # Choose the best date source
        date = filename_date if filename_date else content_date
        
        # Validate date is not Sept 13, 1982 (suspected birthdate)
        if date and date.month == 9 and date.day == 13 and date.year == 1982:
            logger.warning(f"Potential birthdate detected in {filename}, ignoring date")
            date = None
            
        doctor_info = extract_doctor(text)
        record_type = determine_record_type(filename, text)
        diagnoses = extract_diagnoses(text)
        symptoms = extract_symptoms(text)
        medications = extract_medications(text)
        
        # Create a summary of important sections for the content
        content_sections = []
        
        # Add diagnoses section if found
        if diagnoses:
            content_sections.append("DIAGNOSES/ASSESSMENT:\n" + "\n".join([f"- {d}" for d in diagnoses]))
        
        # Add symptoms section if found
        if symptoms:
            content_sections.append("SYMPTOMS/COMPLAINTS:\n" + "\n".join([f"- {s}" for s in symptoms]))
        
        # Add medications section if found
        if medications:
            content_sections.append("MEDICATIONS:\n" + "\n".join([f"- {m}" for m in medications]))
        
        # Add a brief excerpt from the text
        content_sections.append("EXCERPT:\n" + text[:500] + "...")
        
        # Combine sections into content
        content = "\n\n".join(content_sections)
        
        # Prepare record data
        record_data = {
            "date": date,
            "doctor": doctor_info,
            "type": record_type,
            "diagnoses": diagnoses,
            "symptoms": symptoms,
            "medications": medications,
            "content": content
        }
        
        # Create Notion entry
        notion_entry = create_notion_entry(filename, record_data)
        
        return notion_entry
        
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}")
        return None

def main():
    """Main function to process all files and import to Notion."""
    files_processed = 0
    entries_created = 0
    entries_added_to_notion = 0
    all_entries = []
    
    logger.info(f"Starting processing of medical records from {EXTRACTED_TEXT_DIR}")
    
    # Process all text files
    for filepath in EXTRACTED_TEXT_DIR.glob("*.txt"):
        logger.info(f"Processing {filepath.name}")
        
        files_processed += 1
        entry = process_file(filepath)
        
        if entry:
            entries_created += 1
            all_entries.append(entry)
    
    # Quality check - verify no entries with birthdate or unreasonable dates
    logger.info("Performing quality check on date extraction...")
    entries_with_issues = 0
    for i, entry in enumerate(all_entries):
        try:
            entry_date = datetime.datetime.strptime(entry["date"], "%Y-%m-%d")
            
            # Check for suspected birthdates or unlikely dates
            if entry_date.year < 2010 or entry_date.year > 2025:
                entries_with_issues += 1
                logger.warning(f"Entry with unreasonable date found: {entry['title']} - {entry['date']}")
                logger.warning(f"Source file: {entry['source_file']}")
                
                # Date is unreasonable - try to extract better date from the title
                # Many filenames have dates in format MM_DD_YYYY or similar
                date_match = re.search(r'(\d{1,2})[_\-\.](\d{1,2})[_\-\.](\d{2,4})', entry['source_file'])
                if date_match:
                    month, day, year = date_match.groups()
                    if len(year) == 2:
                        year = '20' + year if int(year) < 50 else '19' + year
                        
                    try:
                        new_date = datetime.datetime(int(year), int(month), int(day))
                        if 2010 <= new_date.year <= 2025:
                            all_entries[i]["date"] = new_date.strftime("%Y-%m-%d")
                            logger.info(f"Fixed date for entry: {entry['title']} - now {new_date.strftime('%Y-%m-%d')}")
                    except ValueError:
                        pass
        except Exception as e:
            logger.error(f"Error checking entry date: {e}")
    
    logger.info(f"Quality check complete: {entries_with_issues} entries with date issues found and fixed if possible")
            
    # Add validated entries to Notion if API key is available
    if NOTION_API_KEY:
        for entry in all_entries:
            if add_to_notion_medical_calendar(entry):
                entries_added_to_notion += 1
    
    # Save all entries to JSON for reference
    output_file = OUTPUT_DIR / "medical_calendar_entries.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, indent=2, default=str)
    
    logger.info(f"Processing complete: {files_processed} files processed")
    logger.info(f"Entries created: {entries_created}")
    logger.info(f"Entries added to Notion: {entries_added_to_notion}")
    logger.info(f"All entries saved to {output_file}")

if __name__ == "__main__":
    main() 