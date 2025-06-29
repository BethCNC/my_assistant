#!/usr/bin/env python3
# analyze_medical_text.py - Analyzes extracted text from medical PDFs to identify key information

import os
import re
import json
import glob
from datetime import datetime
from pathlib import Path
import argparse

# Medical entity patterns
PATTERNS = {
    "dates": r"\b(?:\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}|\w+ \d{1,2},? \d{4}|\d{1,2} \w+ \d{4})\b",
    "medical_record_number": r"\bMRN:?\s*(\d{5,10})\b",
    "patient_id": r"\b(?:Patient ID|ID|Record Number):?\s*([A-Z0-9]{5,12})\b",
    "physician": r"(?:Dr\.|Doctor|Physician|Provider):?\s*([A-Z][a-z]+ [A-Z][a-z]+(?:[-][A-Z][a-z]+)?)",
    "diagnosis": r"(?:Diagnosis|Assessment|Impression):(?:\s|\n)+(.*?)(?:\n\n|\n[A-Z])",
    "medications": r"(?:Medications?|Prescription|Current Medications?):(?:\s|\n)+(.*?)(?:\n\n|\n[A-Z])",
    "lab_results": r"(?:Result|Value):?\s*(\d+\.?\d*)\s*(?:mg/dL|mmol/L|U/L|mg/L|ng/mL)",
    "vital_signs": r"(?:BP|Blood Pressure):?\s*(\d{2,3}/\d{2,3})|(?:Temp|Temperature):?\s*(\d{2}\.?\d*)|(?:Pulse|HR):?\s*(\d{2,3})|(?:Resp|RR):?\s*(\d{1,2})",
}

def extract_entities(text, pattern_name, pattern):
    """Extract medical entities from text using regex patterns"""
    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not matches:
        return []
    
    # Process matching depending on pattern
    if pattern_name in ["diagnosis", "medications"]:
        # These can be multiline and need cleaning
        if isinstance(matches[0], str):
            results = [m.strip() for m in matches]
        else:
            # Handle tuple matches
            results = [m[0].strip() for m in matches]
    elif pattern_name == "vital_signs":
        # Handle multiple capture groups
        results = []
        for match in matches:
            if isinstance(match, tuple):
                value = next((m for m in match if m), "")
                if value:
                    results.append(value)
            else:
                results.append(match)
    else:
        # Simple string matches
        results = matches
    
    return results

def analyze_text_file(file_path):
    """Analyze a single text file extracted from a medical PDF"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract filename without extension
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        
        # Extract entities
        results = {
            "file_name": file_name,
            "analysis_date": datetime.now().isoformat(),
            "entities": {}
        }
        
        for entity_name, pattern in PATTERNS.items():
            matches = extract_entities(text, entity_name, pattern)
            results["entities"][entity_name] = matches
        
        # Try to determine document type
        if re.search(r"lab(?:oratory)?\s*results|lab\s*report", text, re.IGNORECASE):
            results["document_type"] = "lab_result"
        elif re.search(r"(?:office|clinic|visit)\s*note", text, re.IGNORECASE):
            results["document_type"] = "visit_note"
        elif re.search(r"discharge\s*summary", text, re.IGNORECASE):
            results["document_type"] = "discharge_summary"
        elif re.search(r"operative\s*(?:report|note)", text, re.IGNORECASE):
            results["document_type"] = "operative_report"
        elif re.search(r"radiology|imaging|x-ray|mri|ct scan", text, re.IGNORECASE):
            results["document_type"] = "radiology_report"
        else:
            results["document_type"] = "unknown"
            
        # Get approximate date of document (first date found)
        dates = results["entities"]["dates"]
        if dates:
            results["document_date"] = dates[0]
        else:
            results["document_date"] = "unknown"
        
        return results
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return {
            "file_name": os.path.basename(file_path),
            "analysis_date": datetime.now().isoformat(),
            "error": str(e)
        }

def main():
    """Main function to analyze all extracted text files"""
    parser = argparse.ArgumentParser(description="Analyze medical text files")
    parser.add_argument("--input-dir", default=None, help="Directory containing extracted text files")
    parser.add_argument("--output-file", default=None, help="JSON file to write analysis results")
    args = parser.parse_args()
    
    # Set default directories if not provided
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    if args.input_dir is None:
        input_dir = os.path.join(base_dir, "data", "extracted_text")
    else:
        input_dir = args.input_dir
    
    if args.output_file is None:
        output_file = os.path.join(base_dir, "data", "analysis_results.json")
    else:
        output_file = args.output_file
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist!")
        return
    
    # Get all text files
    text_files = glob.glob(os.path.join(input_dir, "*.txt"))
    print(f"Found {len(text_files)} text files to analyze")
    
    # Analyze each file
    results = []
    for file_path in text_files:
        print(f"Analyzing {os.path.basename(file_path)}...")
        analysis = analyze_text_file(file_path)
        results.append(analysis)
    
    # Save results to JSON file
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "total_files": len(results),
            "results": results
        }, f, indent=2)
    
    print(f"\nAnalysis complete. Results saved to {output_file}")
    
    # Print some basic stats
    doc_types = {}
    for result in results:
        doc_type = result.get("document_type", "unknown")
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    print("\nDocument types found:")
    for doc_type, count in doc_types.items():
        print(f"  {doc_type}: {count}")

if __name__ == "__main__":
    main() 