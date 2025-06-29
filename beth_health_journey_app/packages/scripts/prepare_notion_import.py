#!/usr/bin/env python3
"""
Notion Import Preparation Script

This script takes the analysis results and formats them for import into Notion,
following the structure outlined in the Notion Project Overview.
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path

# Configuration
ANALYSIS_DIR = "data/analysis_results"
ANALYSIS_SUMMARY_FILE = os.path.join(ANALYSIS_DIR, "analysis_summary.json")
NOTION_IMPORT_DIR = "data/notion_import"
CALENDAR_CSV_FILE = os.path.join(NOTION_IMPORT_DIR, "medical_calendar_import.csv")
SYMPTOMS_CSV_FILE = os.path.join(NOTION_IMPORT_DIR, "symptoms_import.csv")
MEDICATIONS_CSV_FILE = os.path.join(NOTION_IMPORT_DIR, "medications_import.csv")


def ensure_dir_exists(dir_path):
    """Ensure that a directory exists, creating it if necessary."""
    os.makedirs(dir_path, exist_ok=True)


def get_all_analysis_files():
    """Get all analysis JSON files from the analysis directory."""
    analysis_files = []
    for root, _, files in os.walk(ANALYSIS_DIR):
        for file in files:
            if file.endswith("_analysis.json") and file != "analysis_summary.json":
                analysis_files.append(os.path.join(root, file))
    return analysis_files


def load_json_file(file_path):
    """Load a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def format_date(date_str):
    """Format a date string for Notion import."""
    if not date_str:
        return ""
    
    # Try to parse different date formats
    try:
        # Try MM/DD/YYYY
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                month, day, year = parts
                if len(year) == 2:
                    year = "20" + year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Try YYYY-MM-DD
        if "-" in date_str and len(date_str.split("-")[0]) == 4:
            return date_str
        
        # Try Month DD, YYYY
        import re
        month_names = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", 
                      "may": "05", "jun": "06", "jul": "07", "aug": "08", 
                      "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
        
        match = re.match(r'([A-Za-z]+)[a-z]* (\d{1,2}),? (\d{4})', date_str)
        if match:
            month, day, year = match.groups()
            month_num = month_names.get(month.lower()[:3], "01")
            return f"{year}-{month_num}-{day.zfill(2)}"
    except Exception:
        pass
    
    # Return original if parsing fails
    return date_str


def create_calendar_entry(analysis):
    """Create a calendar entry for Notion import."""
    document_type = analysis.get("document_type", "Other")
    date = format_date(analysis.get("date", ""))
    doctor = analysis.get("doctor", "")
    file_path = analysis.get("file_path", "")
    
    # Determine entry type based on document type
    entry_type_mapping = {
        "Lab Result": "Lab Result",
        "Doctor's Notes": "Doctor's Notes - Appt Notes",
        "Imaging": "Imaging",
        "Medication": "Medication Change",
        "Procedure": "Surgery/Procedure",
        "Hospital": "Hospitalization",
        "Other": "Other"
    }
    entry_type = entry_type_mapping.get(document_type, "Other")
    
    # Create title based on document type and date
    if document_type == "Lab Result" and analysis.get("lab_values"):
        # Use the first lab test as the title
        test_name = analysis["lab_values"][0]["test_name"]
        title = f"{test_name} - {date}" if date else test_name
    elif doctor:
        specialty = get_specialty_from_path(file_path)
        title = f"{specialty} Visit - {date}" if date else f"{specialty} Visit"
    else:
        title = f"{document_type} - {date}" if date else document_type
    
    # Create summary content
    content = ""
    if document_type == "Lab Result" and analysis.get("lab_values"):
        content += "Lab Results:\n"
        for lab in analysis["lab_values"]:
            content += f"- {lab['test_name']}: {lab['value']} {lab['unit']}"
            if lab['reference_range']:
                content += f" (Normal range: {lab['reference_range']})"
            content += "\n"
    elif document_type == "Doctor's Notes" and analysis.get("diagnoses"):
        content += "Diagnoses:\n"
        for diagnosis in analysis["diagnoses"]:
            content += f"- {diagnosis}\n"
    
    return {
        "Title": title,
        "Type": entry_type,
        "Date": date,
        "Doctor": doctor,
        "Visit Summary/Lab Result": content,
        "Historical Import": "Yes",
        "Source File": file_path
    }


def get_specialty_from_path(file_path):
    """Extract specialty from the file path."""
    path = Path(file_path)
    parts = path.parts
    
    # Look for specialty folder in path
    for specialty in ["GP", "Endocrinology", "Rheumatology", "Neurology", 
                     "Cardiology", "Orthopedics", "Eye", "Dermatology"]:
        if specialty in parts:
            return specialty
    
    return "Medical"


def extract_symptoms(analysis):
    """Extract symptoms from analysis."""
    symptoms = []
    
    # Extract from doctor's notes - this would need more sophisticated NLP in a real scenario
    if analysis.get("document_type") == "Doctor's Notes":
        # For this simple example, we'll just look for common symptom keywords
        text = read_text_file(analysis["file_path"])
        symptom_keywords = [
            "pain", "fatigue", "weakness", "nausea", "dizziness", 
            "headache", "rash", "fever", "cough", "shortness of breath"
        ]
        
        for keyword in symptom_keywords:
            if keyword in text.lower():
                symptoms.append({
                    "Symptom": keyword.title(),
                    "First Noted": format_date(analysis.get("date", "")),
                    "Status": "Active",
                    "Notes": f"Mentioned in {analysis.get('file_path')}"
                })
    
    return symptoms


def extract_medications(analysis):
    """Extract medications from analysis."""
    medications = []
    
    # Extract from doctor's notes or medication documents
    if analysis.get("document_type") in ["Doctor's Notes", "Medication"]:
        # This would need more sophisticated NLP in a real scenario
        text = read_text_file(analysis["file_path"])
        
        # Simple pattern matching for medication names
        import re
        med_patterns = [
            r'(?:prescribed|started on|taking)\s+([A-Z][a-zA-Z]+(?:\s+\d+\s*(?:mg|mcg|g))?)',
            r'([A-Z][a-zA-Z]+(?:\s+\d+\s*(?:mg|mcg|g)))\s+(?:daily|twice daily|once daily|weekly)'
        ]
        
        for pattern in med_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                medications.append({
                    "Medication": match,
                    "Start Date": format_date(analysis.get("date", "")),
                    "Prescribed By": analysis.get("doctor", ""),
                    "Notes": f"Mentioned in {analysis.get('file_path')}"
                })
    
    return medications


def read_text_file(file_path):
    """Read the original text file corresponding to the analysis file."""
    # Convert analysis file path to original text file path
    if isinstance(file_path, str) and "_analysis.json" in file_path:
        original_path = file_path.replace("_analysis.json", "")
    else:
        # If it's already the path to the text file from the analysis object
        original_path = os.path.join("data/extracted_text", file_path)
    
    try:
        with open(original_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {original_path}: {e}")
        return ""


def write_csv(items, output_file, fieldnames):
    """Write items to a CSV file."""
    with open(output_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def main():
    """Main function to prepare data for Notion import."""
    # Ensure output directory exists
    ensure_dir_exists(NOTION_IMPORT_DIR)
    
    # Get all analysis files
    print("Finding all analysis files...")
    analysis_files = get_all_analysis_files()
    print(f"Found {len(analysis_files)} analysis files.")
    
    # Process each analysis file
    calendar_entries = []
    symptom_entries = []
    medication_entries = []
    
    for file_path in analysis_files:
        analysis = load_json_file(file_path)
        
        # Create calendar entry
        calendar_entry = create_calendar_entry(analysis)
        calendar_entries.append(calendar_entry)
        
        # Extract symptoms
        symptoms = extract_symptoms(analysis)
        symptom_entries.extend(symptoms)
        
        # Extract medications
        medications = extract_medications(analysis)
        medication_entries.extend(medications)
    
    # Write to CSV files
    calendar_fieldnames = ["Title", "Type", "Date", "Doctor", "Visit Summary/Lab Result", 
                          "Historical Import", "Source File"]
    write_csv(calendar_entries, CALENDAR_CSV_FILE, calendar_fieldnames)
    
    symptom_fieldnames = ["Symptom", "First Noted", "Status", "Notes"]
    write_csv(symptom_entries, SYMPTOMS_CSV_FILE, symptom_fieldnames)
    
    medication_fieldnames = ["Medication", "Start Date", "Prescribed By", "Notes"]
    write_csv(medication_entries, MEDICATIONS_CSV_FILE, medication_fieldnames)
    
    print(f"Notion import preparation complete.")
    print(f"Calendar entries: {len(calendar_entries)} (saved to {CALENDAR_CSV_FILE})")
    print(f"Symptom entries: {len(symptom_entries)} (saved to {SYMPTOMS_CSV_FILE})")
    print(f"Medication entries: {len(medication_entries)} (saved to {MEDICATIONS_CSV_FILE})")


if __name__ == "__main__":
    main() 