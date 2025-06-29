#!/usr/bin/env python3
import os
import sys
import re
import csv
import PyPDF2
import argparse
import random
from datetime import datetime
from pathlib import Path

"""
PDF Text Extractor for Medical Records (Test Version)

This script extracts text from PDF files in a specified directory and saves the text 
to a structured CSV file that can be imported into Notion.

CRITICAL: ALL medically relevant information is preserved, nothing is summarized, abbreviated, 
or interpreted in any way. This tool simply extracts raw text from PDFs.

Usage:
    python pdf_extractor.py --input <input_directory> --output <output_csv>

Example:
    python pdf_extractor.py --input "/Users/bethcartrette/REPOS/beth_health_journey_app/data/atrium-exports/all_import" --output "extracted_records.csv"
"""

def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file.
    Returns the raw text and metadata.
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
            
            # Extract creation date if available
            creation_date = None
            if metadata and '/CreationDate' in metadata:
                date_str = metadata['/CreationDate']
                # Try to parse PDF date format (e.g., "D:20210130152951+00'00'")
                if date_str.startswith('D:'):
                    try:
                        # Remove D: prefix and timezone info for simplicity
                        date_str = date_str[2:14]  # Extract YYYYMMDDHHMMSS
                        creation_date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                    except ValueError:
                        pass
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {page_num + 1} ---\n"
                    text += page_text
            
            return {
                "text": text,
                "creation_date": creation_date,
                "page_count": len(reader.pages),
                "metadata": str(metadata) if metadata else ""
            }
    except Exception as e:
        return {
            "text": f"ERROR: Could not extract text: {str(e)}",
            "creation_date": None,
            "page_count": 0,
            "metadata": ""
        }

def detect_document_type(text, file_path=None):
    """
    Attempt to detect the document type based on content and file path.
    Returns one of: "Lab Result", "Doctor's Notes", "Image/Scan", etc.
    """
    # First try to detect from folder structure
    if file_path:
        path_str = str(file_path).lower()
        
        # Check if it's in a specific folder that indicates type
        if 'scan' in path_str or 'imaging' in path_str or 'radiology' in path_str:
            return "Image/Scan"
        elif 'lab' in path_str or 'test' in path_str:
            return "Lab Result"
        elif 'visit' in path_str or 'appointment' in path_str or 'dr ' in path_str or 'doctor' in path_str:
            return "Doctor's Notes"
        elif 'hospital' in path_str or 'admission' in path_str:
            return "Hospitalization"
        elif 'surgery' in path_str or 'procedure' in path_str:
            return "Surgery/Procedure"
    
    # If folder doesn't indicate type, check the content
    text_lower = text.lower()
    
    if re.search(r'lab(oratory)?\s+results?|test\s+results?|t3|t4|tsh|blood test|cbc|complete blood count', text_lower):
        return "Lab Result"
    elif re.search(r'radiology|x-ray|mri|ct\s+scan|ultrasound|imaging|diagnostic imaging', text_lower):
        return "Image/Scan"
    elif re.search(r'operative\s+report|surgery|procedure|surgical|operation', text_lower):
        return "Surgery/Procedure"
    elif re.search(r'admission|discharge\s+summary|hospital|inpatient|admitted', text_lower):
        return "Hospitalization"
    elif re.search(r'follow[-\s]up|assessment|consultation|visit|appointment|exam|evaluation|history|physical', text_lower):
        return "Doctor's Notes"
    else:
        return "Medical Document"

def extract_doctor_name(text, file_path=None):
    """
    Attempt to extract doctor name from the document text and file path.
    Returns the probable doctor name or None if not found.
    """
    # First check if doctor name is in the folder path
    if file_path:
        path_str = str(file_path)
        
        # Look for Dr or Doctor in the path
        dr_pattern = re.search(r'Dr\.?\s*([A-Z][a-z]+)', path_str)
        if dr_pattern:
            return dr_pattern.group(1)
        
        # Look for folder names with format like "06_June 8 2022_Dr Starr"
        folder_pattern = re.search(r'_Dr\.?\s*([A-Z][a-z]+)', path_str)
        if folder_pattern:
            return folder_pattern.group(1)
    
    # If not found in path, check the text content
    # Common patterns for doctor names
    patterns = [
        r'(?:Dr\.|Doctor)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Dr. John Smith
        r'(?:physician|provider|doctor):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Physician: John Smith
        r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(?:MD|M\.D\.|D\.O\.|DO)',  # John Smith, MD
        r'(?:Dr\.|Doctor)\s+([A-Z][a-z]+)',  # Dr. Smith
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    return None

def extract_date_from_text(text, file_path=None):
    """
    Attempt to extract a date from the document text and file path.
    Returns a datetime object or None if no date found.
    """
    # First try to extract date from folder path, which is more reliable
    if file_path:
        path_str = str(file_path)
        
        # Try to find year folder pattern first (e.g., 2022/GP/...)
        year_pattern = re.search(r'/(\d{4})/', path_str)
        if year_pattern:
            year = int(year_pattern.group(1))
            
            # Look for month/day patterns in folder names like "06_June 8 2022_Dr Starr"
            date_pattern = re.search(r'(\d{1,2})_([A-Za-z]+)\s+(\d{1,2})', path_str)
            if date_pattern:
                try:
                    month_num = int(date_pattern.group(1))
                    day = int(date_pattern.group(3))
                    return datetime(year, month_num, day)
                except ValueError:
                    pass
            
            # Try matching month name pattern like "June 8 2022"
            month_name_pattern = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})\s+\d{4}', path_str, re.IGNORECASE)
            if month_name_pattern:
                try:
                    month_str = month_name_pattern.group(1)
                    day = int(month_name_pattern.group(2))
                    month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 
                                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                    month_num = month_map[month_str.lower()[:3]]
                    return datetime(year, month_num, day)
                except (ValueError, KeyError):
                    pass
    
    # If no date found in path, look in the document text
    # Common date patterns
    patterns = [
        r'(?:Date:|\bDate\b)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # Date: MM/DD/YYYY
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # January 1, 2020
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Try to parse the date (would need more sophisticated parsing for all formats)
            try:
                # Simple parsing for MM/DD/YYYY format
                if '/' in matches[0]:
                    parts = matches[0].split('/')
                    if len(parts) == 3:
                        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                        if year < 100:  # Two-digit year
                            year += 2000 if year < 50 else 1900
                        return datetime(year, month, day)
                return None
            except ValueError:
                continue
    
    return None

def process_test_samples(directory_path, output_csv, sample_count=3, year_folder=None):
    """
    Process a few random PDF files as a test.
    Saves results to a CSV file.
    """
    directory_path = Path(directory_path)
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_csv).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    # Find all PDF files
    if year_folder:
        year_path = directory_path / year_folder
        if not year_path.exists():
            print(f"Year folder {year_folder} not found")
            return
        pdf_files = list(year_path.glob('**/*.pdf'))
    else:
        pdf_files = list(directory_path.glob('**/*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return
    
    total_files = len(pdf_files)
    print(f"Found {total_files} PDF files. Selecting {min(sample_count, total_files)} for testing.")
    
    # Select random samples
    samples = random.sample(pdf_files, min(sample_count, total_files))
    
    # Initialize CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'File Name', 
            'Directory', 
            'Date', 
            'Type', 
            'Doctor', 
            'Page Count', 
            'Metadata',
            'Full Text',
            'Specialty',  # New field for the specialty/department
            'Year'        # New field for the year
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each PDF file
        for i, pdf_path in enumerate(samples):
            print(f"Processing test sample {i+1}/{len(samples)}: {pdf_path.name}")
            
            try:
                # Extract text and metadata
                result = extract_text_from_pdf(pdf_path)
                text = result["text"]
                
                # Get specialty and year from path
                path_parts = str(pdf_path.relative_to(directory_path)).split(os.sep)
                year = path_parts[0] if len(path_parts) > 0 and path_parts[0].isdigit() else ""
                specialty = path_parts[1] if len(path_parts) > 1 else ""
                
                # Detect document properties using file path
                doc_type = detect_document_type(text, pdf_path)
                doctor = extract_doctor_name(text, pdf_path)
                
                # Determine date from metadata, path, or text
                date = result["creation_date"]
                if not date:
                    date = extract_date_from_text(text, pdf_path)
                date_str = date.strftime('%Y-%m-%d') if date else ""
                
                # Write to CSV
                writer.writerow({
                    'File Name': pdf_path.name,
                    'Directory': str(pdf_path.parent.relative_to(directory_path)),
                    'Date': date_str,
                    'Type': doc_type,
                    'Doctor': doctor if doctor else "",
                    'Page Count': result["page_count"],
                    'Metadata': result["metadata"],
                    'Full Text': text,
                    'Specialty': specialty,
                    'Year': year
                })
                
                # Additionally, save the extracted text to a text file in the same directory
                text_dir = directory_path.parent / "extracted_text"
                if not text_dir.exists():
                    text_dir.mkdir(parents=True)
                
                # Preserve the folder structure
                relative_path = pdf_path.relative_to(directory_path)
                output_text_dir = text_dir / relative_path.parent
                if not output_text_dir.exists():
                    output_text_dir.mkdir(parents=True, exist_ok=True)
                
                # Save the text file
                text_file_path = output_text_dir / f"{pdf_path.stem}.txt"
                with open(text_file_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(f"Filename: {pdf_path.name}\n")
                    text_file.write(f"Date: {date_str}\n")
                    text_file.write(f"Type: {doc_type}\n")
                    text_file.write(f"Doctor: {doctor if doctor else 'Unknown'}\n")
                    text_file.write(f"Specialty: {specialty}\n")
                    text_file.write(f"Year: {year}\n")
                    text_file.write("\n--- EXTRACTED TEXT ---\n\n")
                    text_file.write(text)
                
            except Exception as e:
                print(f"Error processing {pdf_path.name}: {str(e)}")
                # Write error record
                writer.writerow({
                    'File Name': pdf_path.name,
                    'Directory': str(pdf_path.parent.relative_to(directory_path)),
                    'Date': "",
                    'Type': "ERROR",
                    'Doctor': "",
                    'Page Count': 0,
                    'Metadata': str(e),
                    'Full Text': f"Error processing file: {str(e)}",
                    'Specialty': specialty if 'specialty' in locals() else "",
                    'Year': year if 'year' in locals() else ""
                })
    
    print(f"Test extraction complete. Results saved to {output_csv}")
    print(f"Individual text files saved in {text_dir}")

def process_directory(directory_path, output_csv, year_folder=None):
    """
    Process all PDF files in the given directory and its subdirectories.
    Saves results to a CSV file.
    """
    directory_path = Path(directory_path)
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_csv).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    # Create directory for extracted text files
    text_dir = directory_path.parent / "extracted_text"
    if not text_dir.exists():
        text_dir.mkdir(parents=True)
    
    # Find all PDF files
    if year_folder:
        year_path = directory_path / year_folder
        if not year_path.exists():
            print(f"Year folder {year_folder} not found")
            return
        pdf_files = list(year_path.glob('**/*.pdf'))
    else:
        pdf_files = list(directory_path.glob('**/*.pdf'))
        
    total_files = len(pdf_files)
    
    print(f"Found {total_files} PDF files to process.")
    
    # Initialize CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'File Name', 
            'Directory', 
            'Date', 
            'Type', 
            'Doctor', 
            'Page Count', 
            'Metadata',
            'Full Text',
            'Specialty',  # New field for the specialty/department
            'Year'        # New field for the year
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each PDF file
        for i, pdf_path in enumerate(pdf_files):
            print(f"Processing {i+1}/{total_files}: {pdf_path.name}")
            
            try:
                # Extract text and metadata
                result = extract_text_from_pdf(pdf_path)
                text = result["text"]
                
                # Get specialty and year from path
                path_parts = str(pdf_path.relative_to(directory_path)).split(os.sep)
                year = path_parts[0] if len(path_parts) > 0 and path_parts[0].isdigit() else ""
                specialty = path_parts[1] if len(path_parts) > 1 else ""
                
                # Detect document properties using file path
                doc_type = detect_document_type(text, pdf_path)
                doctor = extract_doctor_name(text, pdf_path)
                
                # Determine date from metadata, path, or text
                date = result["creation_date"]
                if not date:
                    date = extract_date_from_text(text, pdf_path)
                date_str = date.strftime('%Y-%m-%d') if date else ""
                
                # Write to CSV
                writer.writerow({
                    'File Name': pdf_path.name,
                    'Directory': str(pdf_path.parent.relative_to(directory_path)),
                    'Date': date_str,
                    'Type': doc_type,
                    'Doctor': doctor if doctor else "",
                    'Page Count': result["page_count"],
                    'Metadata': result["metadata"],
                    'Full Text': text,
                    'Specialty': specialty,
                    'Year': year
                })
                
                # Additionally, save the extracted text to a text file in the same directory
                # Preserve the folder structure
                relative_path = pdf_path.relative_to(directory_path)
                output_text_dir = text_dir / relative_path.parent
                if not output_text_dir.exists():
                    output_text_dir.mkdir(parents=True, exist_ok=True)
                
                # Save the text file
                text_file_path = output_text_dir / f"{pdf_path.stem}.txt"
                with open(text_file_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(f"Filename: {pdf_path.name}\n")
                    text_file.write(f"Date: {date_str}\n")
                    text_file.write(f"Type: {doc_type}\n")
                    text_file.write(f"Doctor: {doctor if doctor else 'Unknown'}\n")
                    text_file.write(f"Specialty: {specialty}\n")
                    text_file.write(f"Year: {year}\n")
                    text_file.write("\n--- EXTRACTED TEXT ---\n\n")
                    text_file.write(text)
                
            except Exception as e:
                print(f"Error processing {pdf_path.name}: {str(e)}")
                # Write error record
                writer.writerow({
                    'File Name': pdf_path.name,
                    'Directory': str(pdf_path.parent.relative_to(directory_path)),
                    'Date': "",
                    'Type': "ERROR",
                    'Doctor': "",
                    'Page Count': 0,
                    'Metadata': str(e),
                    'Full Text': f"Error processing file: {str(e)}",
                    'Specialty': specialty if 'specialty' in locals() else "",
                    'Year': year if 'year' in locals() else ""
                })
    
    print(f"Extraction complete. Results saved to {output_csv}")
    print(f"Individual text files saved in {text_dir}")

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF medical records")
    parser.add_argument("--input", required=True, help="Directory containing PDF files")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument("--test", action="store_true", help="Run in test mode with only a few samples")
    parser.add_argument("--sample", type=int, default=3, help="Number of sample files to process in test mode")
    parser.add_argument("--year", help="Optional: specific year folder to process")
    args = parser.parse_args()
    
    input_directory = args.input
    output_csv = args.output
    
    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory")
        sys.exit(1)
    
    # Test mode: Process only a few random files
    if args.test:
        process_test_samples(input_directory, output_csv, args.sample, args.year)
    else:
        process_directory(input_directory, output_csv, args.year)

if __name__ == "__main__":
    main()