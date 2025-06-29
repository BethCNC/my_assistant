#!/usr/bin/env python3
"""
Medical Text Analysis Script

This script analyzes the extracted text from PDF files to identify
and categorize medical information for import into Notion.
"""

import os
import json
import re
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict, Counter

# Configuration
EXTRACTED_TEXT_DIR = "data/extracted_text"
METADATA_FILE = os.path.join(EXTRACTED_TEXT_DIR, "pdf_metadata.json")
ANALYSIS_OUTPUT_DIR = "data/analysis_results"
ANALYSIS_SUMMARY_FILE = os.path.join(ANALYSIS_OUTPUT_DIR, "analysis_summary.json")


def ensure_dir_exists(dir_path):
    """Ensure that a directory exists, creating it if necessary."""
    os.makedirs(dir_path, exist_ok=True)


def load_metadata():
    """Load metadata from the metadata file."""
    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def read_text_file(file_path):
    """Read text from a file."""
    full_path = os.path.join(EXTRACTED_TEXT_DIR, file_path)
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {full_path}: {e}")
        return ""


def identify_document_type(text):
    """Identify the type of medical document based on text content."""
    text_lower = text.lower()
    
    if any(x in text_lower for x in ['lab result', 'laboratory', 'test result', 'specimen']):
        return "Lab Result"
    elif any(x in text_lower for x in ['diagnosis', 'assessment', 'plan', 'chief complaint']):
        return "Doctor's Notes"
    elif any(x in text_lower for x in ['radiology', 'x-ray', 'mri', 'ct scan', 'ultrasound']):
        return "Imaging"
    elif any(x in text_lower for x in ['medication', 'prescription', 'dosage', 'pharmacy']):
        return "Medication"
    elif any(x in text_lower for x in ['surgery', 'procedure', 'operation']):
        return "Procedure"
    elif any(x in text_lower for x in ['discharge', 'admission', 'hospital']):
        return "Hospital"
    else:
        return "Other"


def extract_date(text):
    """Extract a date from the text using regex patterns."""
    # Try to match common date formats
    date_patterns = [
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    
    return None


def extract_doctor_name(text):
    """Extract doctor name from the text."""
    # Look for patterns like "Dr. Smith" or "Physician: Smith"
    dr_pattern = r'Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    physician_pattern = r'Physician:?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    
    dr_matches = re.findall(dr_pattern, text)
    if dr_matches:
        return dr_matches[0]
    
    physician_matches = re.findall(physician_pattern, text)
    if physician_matches:
        return physician_matches[0]
    
    return None


def extract_lab_values(text):
    """Extract lab values and reference ranges from the text."""
    lab_values = []
    
    # Pattern for lab values: test name followed by value and optional units and reference range
    lab_pattern = r'([A-Za-z\s]+):\s*(\d+\.?\d*)\s*([a-zA-Z%/]*)\s*(?:Reference Range:?\s*([^\\n]+))?'
    
    matches = re.findall(lab_pattern, text)
    for match in matches:
        test_name, value, unit, ref_range = match
        lab_values.append({
            "test_name": test_name.strip(),
            "value": value,
            "unit": unit,
            "reference_range": ref_range.strip() if ref_range else None
        })
    
    return lab_values


def extract_diagnoses(text):
    """Extract diagnoses from the text."""
    diagnoses = []
    
    # Pattern for diagnoses sections
    diagnosis_sections = re.findall(r'Diagnosis(?:es)?:?\s*([^\\n]+(?:\\n[^\\n]+)*)', text)
    
    for section in diagnosis_sections:
        # Split by newlines or semicolons
        items = re.split(r'[;\n]', section)
        for item in items:
            if item.strip():
                diagnoses.append(item.strip())
    
    return diagnoses


def analyze_text_file(text_path):
    """Analyze a single text file and extract relevant information."""
    text = read_text_file(text_path)
    if not text:
        return None
    
    # Basic analysis
    document_type = identify_document_type(text)
    date = extract_date(text)
    doctor = extract_doctor_name(text)
    
    # Type-specific analysis
    analysis = {
        "document_type": document_type,
        "date": date,
        "doctor": doctor,
        "word_count": len(text.split()),
        "character_count": len(text)
    }
    
    # Extract additional information based on document type
    if document_type == "Lab Result":
        analysis["lab_values"] = extract_lab_values(text)
    elif document_type == "Doctor's Notes":
        analysis["diagnoses"] = extract_diagnoses(text)
    
    return analysis


def main():
    """Main function to analyze all extracted text files."""
    # Ensure output directory exists
    ensure_dir_exists(ANALYSIS_OUTPUT_DIR)
    
    # Load metadata
    print("Loading metadata...")
    metadata = load_metadata()
    
    # Get all text files from metadata
    text_files = [pdf["extracted_text_path"] for pdf in metadata["pdfs"] 
                  if pdf["extraction_status"] == "success"]
    print(f"Found {len(text_files)} text files to analyze.")
    
    # Analyze each text file
    results = []
    for text_path in tqdm(text_files, desc="Analyzing text"):
        analysis = analyze_text_file(text_path)
        if analysis:
            analysis["file_path"] = text_path
            results.append(analysis)
    
    # Generate summary statistics
    summary = {
        "total_files": len(results),
        "document_types": Counter([r["document_type"] for r in results]),
        "doctors": Counter([r["doctor"] for r in results if r["doctor"]]),
        "by_year": defaultdict(int)
    }
    
    # Count files by year
    for pdf in metadata["pdfs"]:
        if pdf["year_folder"]:
            try:
                year = int(pdf["year_folder"])
                summary["by_year"][str(year)] += 1
            except ValueError:
                pass
    
    # Convert defaultdict to regular dict for JSON serialization
    summary["by_year"] = dict(summary["by_year"])
    
    # Save each analysis result to a separate file
    for result in results:
        file_path = result["file_path"]
        output_path = os.path.join(ANALYSIS_OUTPUT_DIR, 
                                  os.path.splitext(file_path)[0] + "_analysis.json")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)
    
    # Save summary
    with open(ANALYSIS_SUMMARY_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)
    
    print(f"Analysis complete. Summary saved to {ANALYSIS_SUMMARY_FILE}")
    print(f"Individual analyses saved to {ANALYSIS_OUTPUT_DIR}")


if __name__ == "__main__":
    main() 