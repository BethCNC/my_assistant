#!/usr/bin/env python3
"""
Script to extract medications from medical records and import them into the Medications database.

This script reads the extracted text files, identifies medications,
and adds them to the Medications database in Notion.
"""

import os
import re
import json
import datetime
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
EXTRACTED_TEXT_DIR = "data/extracted_text"
OUTPUT_DIR = "data/notion_import_ready"
MEDICATIONS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "medication_entries.json")

# Notion API configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
MEDICATIONS_DB_ID = "17b86edcae2c81a7b28ae9fbcc7e7b62"
DOCTOR_DB_ID = "17b86edcae2c81558caafbb80647f6a9"

# Notion API endpoints
NOTION_API_BASE = "https://api.notion.com/v1"
PAGES_ENDPOINT = f"{NOTION_API_BASE}/pages"
MEDICATIONS_QUERY_ENDPOINT = f"{NOTION_API_BASE}/databases/{MEDICATIONS_DB_ID}/query"
DOCTORS_QUERY_ENDPOINT = f"{NOTION_API_BASE}/databases/{DOCTOR_DB_ID}/query"

# Common medications to look for - extend this list as needed
COMMON_MEDICATIONS = [
    "Methotrexate", "Humira", "Enbrel", "Plaquenil", "Prednisone", "Synthroid", 
    "Levothyroxine", "Adderall", "Zoloft", "Lexapro", "Wellbutrin", "Cymbalta",
    "Gabapentin", "Lyrica", "Trazodone", "Seroquel", "Abilify", "Ritalin",
    "Concerta", "Lamictal", "Lithium", "Xanax", "Klonopin", "Ativan", 
    "Ambien", "Lunesta", "Zyrtec", "Claritin", "Flonase", "Advair", 
    "Albuterol", "Singulair", "Protonix", "Nexium", "Prilosec", "Zantac",
    "Lisinopril", "Metoprolol", "Amlodipine", "Lipitor", "Crestor", "Metformin"
]

# Medication section headers to look for
MEDICATION_HEADERS = [
    "Medications:", 
    "Current Medications:", 
    "Prescribed Medications:",
    "Active Medications:",
    "Home Medications:",
    "Outpatient Medications:"
]

# Medication context phrases that indicate a medication is being prescribed/taken
MEDICATION_CONTEXTS = [
    "prescribed", "taking", "takes", "started on", "continues on",
    "dose", "started", "using", "given", "instructed to take"
]

def ensure_dir_exists(dir_path):
    """Ensure that a directory exists, creating it if necessary."""
    os.makedirs(dir_path, exist_ok=True)

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

def find_medication_section(text):
    """Find a dedicated medication section in the text."""
    medication_section = None
    
    # Try to find a medications section
    for section_header in MEDICATION_HEADERS:
        if section_header in text:
            section_start = text.find(section_header) + len(section_header)
            
            # Find the end of the section (next header or double newline)
            next_header_pos = float('inf')
            for next_header in ["Allergies:", "Assessment:", "Plan:", "Review of Systems:", "Physical Exam:", "Diagnosis:"]:
                pos = text.find(next_header, section_start)
                if pos != -1 and pos < next_header_pos:
                    next_header_pos = pos
            
            section_end = text.find("\n\n", section_start)
            
            # If we found a header after our section, use that as the end
            if next_header_pos < float('inf'):
                if section_end == -1 or next_header_pos < section_end:
                    section_end = next_header_pos
            
            # If no double newline or next header, take rest of text
            if section_end == -1:
                section_end = len(text)
                
            medication_section = text[section_start:section_end].strip()
            break
    
    return medication_section

def extract_medications(text):
    """Extract medications from text content."""
    medications = []
    
    # Find a dedicated medication section
    medication_section = find_medication_section(text)
    
    # Process the medication section if found
    if medication_section:
        # Split by newlines or bullet points to get individual medications
        med_lines = re.split(r'[\n•]', medication_section)
        
        for line in med_lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are likely not medications
            if re.search(r'(allergies|diagnosis|assessment|none|denied|no known|nkda)', line, re.IGNORECASE):
                continue
                
            # Extract medication name, dosage, and frequency
            # Example patterns: "Medication 10mg daily" or "Medication (10 mg) twice daily"
            med_match = re.match(r'([A-Za-z\s\-]+)\s*(?:\(?\s*([\d\.]+\s*[a-zA-Z]+)\s*\)?)?(?:\s*(daily|twice daily|weekly|as needed|prn|every \d+ hours|once daily|BID|TID|QID))?', line)
            
            if med_match:
                medication = {
                    "name": med_match.group(1).strip(),
                    "dosage": med_match.group(2).strip() if med_match.group(2) else "",
                    "frequency": med_match.group(3).strip() if med_match.group(3) else ""
                }
                medications.append(medication)
            else:
                # More relaxed pattern as a fallback
                words = line.split()
                if words and any(word.lower() in ["mg", "mcg", "ml", "tablet", "capsule"] for word in words):
                    medications.append({"name": words[0], "dosage": " ".join(words[1:3]), "frequency": ""})
    
    # If no medication section was found, look for medications in context
    # This is much more selective than before to avoid false positives
    if not medications:
        for med in COMMON_MEDICATIONS:
            # Look for a medication only if it appears in a context that suggests it's prescribed
            for context in MEDICATION_CONTEXTS:
                # Pattern looks for context phrases near medication names
                pattern = rf'({context})\s+([A-Za-z\s]{{0,30}})?{med}\b|\b{med}\b([A-Za-z\s]{{0,30}})?\s+({context})'
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                if matches:
                    # Look for dosage near the mention
                    for match in matches:
                        # Find the position of the medication in the text
                        med_pos = text.lower().find(med.lower())
                        
                        # Look for dosage within 50 characters after the medication name
                        context_text = text[med_pos:med_pos+50] if med_pos != -1 else ""
                        
                        # Extract dosage if present
                        dosage_match = re.search(r'([\d\.]+\s*[a-zA-Z]+)', context_text)
                        dosage = dosage_match.group(1) if dosage_match else ""
                        
                        # Extract frequency if present
                        freq_match = re.search(r'(daily|twice daily|weekly|as needed|prn|BID|TID|QID)', context_text, re.IGNORECASE)
                        frequency = freq_match.group(1) if freq_match else ""
                        
                        medications.append({"name": med, "dosage": dosage, "frequency": frequency})
                        # Only add once even if multiple matches
                        break
    
    # Remove duplicate medications (same name)
    unique_meds = []
    med_names = set()
    
    for med in medications:
        if med["name"].lower() not in med_names:
            med_names.add(med["name"].lower())
            unique_meds.append(med)
    
    return unique_meds

def create_medication_entry(medication, source_file, provider=None, date=None):
    """Create an entry for the Medications database."""
    # Basic entry with required fields
    entry = {
        "name": medication["name"],
        "dosage": medication["dosage"],
        "frequency": medication["frequency"],
        "source_file": source_file
    }
    
    # Add optional fields if available
    if provider:
        entry["prescribed_by"] = provider
    
    if date:
        entry["date_prescribed"] = date
    
    return entry

def create_medication_in_notion(entry):
    """Create a medication record in the Notion Medications database."""
    headers = get_notion_headers()
    
    # Get doctor ID if available
    doctor_id = None
    if entry.get("prescribed_by"):
        doctor_id = get_doctor_id_by_name(entry["prescribed_by"])
    
    # Prepare properties for Notion
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": entry["name"]
                    }
                }
            ]
        }
    }
    
    # Add dosage if available
    if entry.get("dosage"):
        properties["Dosage"] = {
            "rich_text": [
                {
                    "text": {
                        "content": entry["dosage"]
                    }
                }
            ]
        }
    
    # Add frequency if available
    if entry.get("frequency"):
        properties["Frequency"] = {
            "rich_text": [
                {
                    "text": {
                        "content": entry["frequency"]
                    }
                }
            ]
        }
    
    # Add date if available
    if entry.get("date_prescribed"):
        properties["Date Started"] = {
            "date": {
                "start": entry["date_prescribed"]
            }
        }
    
    # Add prescribing doctor if available
    if doctor_id:
        properties["Prescribed By"] = {
            "relation": [
                {
                    "id": doctor_id
                }
            ]
        }
    
    # Create page in Notion
    payload = {
        "parent": {
            "database_id": MEDICATIONS_DB_ID
        },
        "properties": properties
    }
    
    response = requests.post(PAGES_ENDPOINT, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error creating medication: {response.text}")
        return False
    
    return True

def main():
    """Main function to extract medications and import them to Notion."""
    print("Starting medication extraction from medical records...")
    
    # Ensure output directory exists
    ensure_dir_exists(OUTPUT_DIR)
    
    # Get list of all extracted text files
    all_text_files = [f for f in os.listdir(EXTRACTED_TEXT_DIR) if f.endswith('.txt')]
    
    # Process each file to extract medications
    medication_entries = []
    
    for filename in all_text_files:
        file_path = os.path.join(EXTRACTED_TEXT_DIR, filename)
        print(f"Processing {filename} for medications...")
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            file_text = file.read()
        
        # Extract medications
        medications = extract_medications(file_text)
        
        if medications:
            print(f"  Found {len(medications)} medications in {filename}")
            
            # Get metadata from filename if possible (matches pattern like YYYY_MM_DD)
            date_match = re.search(r'(\d{4})[_-](\d{2})[_-](\d{2})', filename)
            date = None
            if date_match:
                date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            
            # Try to find provider name in the text
            provider_match = re.search(r'(Dr\.\s*[A-Za-z]+)', file_text)
            provider = provider_match.group(1) if provider_match else None
            
            # Create entries for each medication
            for medication in medications:
                entry = create_medication_entry(medication, filename, provider, date)
                medication_entries.append(entry)
    
    # Write medications to JSON file
    with open(MEDICATIONS_OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        json.dump(medication_entries, outfile, indent=2)
    
    print(f"Extracted {len(medication_entries)} medications from medical records.")
    print(f"Medication data saved to {MEDICATIONS_OUTPUT_FILE}")
    
    # Import medications to Notion if API key is available
    if NOTION_API_KEY:
        import_count = 0
        print("Starting import to Notion Medications database...")
        
        for i, entry in enumerate(medication_entries):
            print(f"Importing medication {i+1}/{len(medication_entries)}: {entry['name']}")
            if create_medication_in_notion(entry):
                import_count += 1
        
        print(f"Import complete. Successfully imported {import_count}/{len(medication_entries)} medications.")
    else:
        print("Notion API key not found. To import medications to Notion, set NOTION_API_KEY environment variable.")

if __name__ == "__main__":
    main() 