#!/usr/bin/env python3
"""
Script to process 2018-2019 medical records and prepare them for Notion import.

This script will:
1. Identify and process extracted text files from 2018 and 2019
2. Format them according to the standard naming convention
3. Prepare them for import into the Medical Calendar database in Notion
"""

import os
import re
import json
import datetime
from pathlib import Path

# Configuration
EXTRACTED_TEXT_DIR = "data/extracted_text"
PDF_DIR = "data/atrium-exports/all_import"
OUTPUT_DIR = "data/notion_import_ready"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "notion_ready_entries.json")

# Mapping from original filenames to dates and record types
# This is needed because the extracted text might not contain clear date information
RECORD_MAP = {
    "XR_WRIST_3_VIEWS_LEFT.txt": {"date": "2019-10-18", "provider": "Dr. Starr", "type": "Imaging", "specialty": "GP"},
    "11-26-2019_hand_Doctor.txt": {"date": "2019-11-26", "provider": "Dr. Valentine", "type": "Doctor's Notes", "specialty": "Hand Doc"},
    # Files from 2018 Endocrinology
    "FREE_T4.txt": {"date": "2018-04-10", "provider": "Dr. Kahn", "type": "Lab Result", "specialty": "Endocrinology"},
    "TSH.txt": {"date": "2018-04-10", "provider": "Dr. Kahn", "type": "Lab Result", "specialty": "Endocrinology"},
    "THYROID_STIMULATING_IMMUNOGLOBULIN.txt": {"date": "2018-04-10", "provider": "Dr. Kahn", "type": "Lab Result", "specialty": "Endocrinology"},
    "THYROTROPIN_RECEPTORAB.txt": {"date": "2018-04-10", "provider": "Dr. Kahn", "type": "Lab Result", "specialty": "Endocrinology"},
    "NM_THYROID_I-131_UPTAKE_AND_SCAN.txt": {"date": "2018-04-10", "provider": "Dr. Kahn", "type": "Imaging", "specialty": "Endocrinology"},
    # Files from 2018 GP
    "MRI_ORBITS_WO_W_CONTRAST.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Imaging", "specialty": "GP"},
    "XR_SHOULDER_2_VIEWS_RIGHT.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Imaging", "specialty": "GP"},
    "THYROGLOBULIN_ANTIBODY.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"},
    "THYROID_PEROXIDASE_AB.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"},
    "HEMOGLOBIN_A1C.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"},
    "LIPID_PANEL_WCHOLHDL_RATIO.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"},
    "COMPREHENSIVE_METABOLIC_PANEL.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"},
    "CBC_WITH_DIFFERENTIAL.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"},
    "T3.txt": {"date": "2018-02-14", "provider": "Dr. LiCause", "type": "Lab Result", "specialty": "GP"}
}

def ensure_dir_exists(dir_path):
    """Ensure that a directory exists, creating it if necessary."""
    os.makedirs(dir_path, exist_ok=True)

def extract_patient_info(text):
    """Extract patient information from text."""
    name_match = re.search(r'Name:\s*([\w\s]+)', text)
    dob_match = re.search(r'DOB:\s*([\d/]+)', text)
    mrn_match = re.search(r'MRN:\s*([\d]+)', text)
    
    patient_info = {}
    if name_match:
        patient_info["name"] = name_match.group(1).strip()
    if dob_match:
        patient_info["dob"] = dob_match.group(1).strip()
    if mrn_match:
        patient_info["mrn"] = mrn_match.group(1).strip()
    
    return patient_info

def extract_lab_values(text):
    """Extract lab test values from text."""
    lab_values = []
    
    # Look for patterns like "Test Name: 1.2 mg/dL (Reference Range: 0.8-1.8)"
    lab_pattern = re.compile(r'([A-Za-z\s\-]+):\s*([\d\.]+)\s*([A-Za-z/%]+)?\s*(?:\(Reference\s*Range:?\s*([\d\.\-]+)\))?')
    
    for match in lab_pattern.finditer(text):
        lab_values.append({
            "test_name": match.group(1).strip(),
            "value": match.group(2).strip(),
            "unit": match.group(3).strip() if match.group(3) else "",
            "reference_range": match.group(4).strip() if match.group(4) else ""
        })
    
    return lab_values

def extract_diagnoses(text):
    """Extract diagnoses from text."""
    diagnoses = []
    
    # Look for patterns like "Diagnosis:" or "Impression:" followed by list items
    sections = re.split(r'(?:Diagnosis|Impression|Assessment):', text)
    if len(sections) > 1:
        diagnosis_section = sections[1].split('\n\n')[0]
        diagnosis_items = re.findall(r'\d+\.\s*([^\n]+)', diagnosis_section)
        
        for item in diagnosis_items:
            diagnoses.append(item.strip())
    
    return diagnoses

def create_notion_entry(filename, file_info, file_text):
    """Create a Notion entry for a medical record."""
    # Extract metadata
    date = file_info.get("date", "")
    provider = file_info.get("provider", "")
    record_type = file_info.get("type", "Other")
    specialty = file_info.get("specialty", "")
    
    # Extract patient info
    patient_info = extract_patient_info(file_text)
    
    # Create title based on type and date
    if record_type == "Lab Result":
        title = f"{date}_Lab_{Path(filename).stem}_{provider.split()[-1]}"
    elif record_type == "Imaging":
        imaging_type = Path(filename).stem.replace("_", " ")
        title = f"{date}_Imaging_{imaging_type}_{provider.split()[-1]}"
    else:
        title = f"{date}_{specialty}_{provider.split()[-1]}"
    
    # Extract content based on record type
    content = ""
    if record_type == "Lab Result":
        content += "Lab Results:\n\n"
        lab_values = extract_lab_values(file_text)
        for lab in lab_values:
            content += f"{lab['test_name']}: {lab['value']} {lab['unit']}"
            if lab['reference_range']:
                content += f" (Normal range: {lab['reference_range']})"
            content += "\n"
    elif record_type == "Doctor's Notes":
        content += "Provider Notes:\n\n"
        diagnoses = extract_diagnoses(file_text)
        if diagnoses:
            content += "Diagnoses:\n"
            for diagnosis in diagnoses:
                content += f"- {diagnosis}\n"
        
        # Add excerpts from the notes
        impression_match = re.search(r'Impression:(.*?)(?:\n\n|$)', file_text, re.DOTALL)
        if impression_match:
            content += "\nImpression:\n" + impression_match.group(1).strip() + "\n"
        
        assessment_match = re.search(r'Assessment:(.*?)(?:\n\n|$)', file_text, re.DOTALL)
        if assessment_match:
            content += "\nAssessment:\n" + assessment_match.group(1).strip() + "\n"
    elif record_type == "Imaging":
        content += "Imaging Results:\n\n"
        
        impression_match = re.search(r'Impression:(.*?)(?:\n\n|$)', file_text, re.DOTALL)
        if impression_match:
            content += "Impression:\n" + impression_match.group(1).strip() + "\n"
        
        narrative_match = re.search(r'Narrative:(.*?)(?:\n\n|$)', file_text, re.DOTALL)
        if narrative_match:
            content += "\nNarrative:\n" + narrative_match.group(1).strip() + "\n"
    
    # Create entry for Notion import
    entry = {
        "title": title,
        "date": date,
        "doctor": provider,
        "type": record_type,
        "content": content,
        "source_file": filename
    }
    
    return entry

def main():
    """Main function to process records and prepare for Notion import."""
    print("Starting to process 2018-2019 medical records...")
    
    # Ensure output directory exists
    ensure_dir_exists(OUTPUT_DIR)
    
    # Get list of all extracted text files
    all_text_files = os.listdir(EXTRACTED_TEXT_DIR)
    
    # Filter for files in our mapping (2018-2019 records)
    entries = []
    for filename in all_text_files:
        if filename in RECORD_MAP:
            print(f"Processing {filename}...")
            
            # Read the file content
            with open(os.path.join(EXTRACTED_TEXT_DIR, filename), 'r', encoding='utf-8') as file:
                file_text = file.read()
            
            # Create Notion entry
            entry = create_notion_entry(filename, RECORD_MAP[filename], file_text)
            entries.append(entry)
    
    # Write entries to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        json.dump(entries, outfile, indent=2)
    
    print(f"Processed {len(entries)} records from 2018-2019.")
    print(f"Notion import data saved to {OUTPUT_FILE}")
    print("To import these records into Notion, run: NOTION_API_KEY=your_key python notion_importer.py")

if __name__ == "__main__":
    main() 