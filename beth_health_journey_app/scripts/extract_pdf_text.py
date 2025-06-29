#!/usr/bin/env python3
# extract_pdf_text.py - Extracts text from PDF files and saves to text files

import os
import sys
import PyPDF2
import glob
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path, output_dir):
    """
    Extract text from a PDF file and save it to a text file.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the extracted text
    
    Returns:
        Path to the created text file
    """
    # Create output filename based on PDF filename
    pdf_filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(pdf_filename)[0]
    # Clean filename to remove special characters
    base_name = re.sub(r'[^\w\s-]', '', base_name).strip().replace(' ', '_')
    output_file = os.path.join(output_dir, f"{base_name}.txt")
    
    try:
        # Open PDF file
        pdf_file_obj = open(pdf_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        
        # Extract text from each page
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page_obj = pdf_reader.pages[page_num]
            page_text = page_obj.extract_text()
            if page_text:
                text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
        
        # Close the PDF file
        pdf_file_obj.close()
        
        # Save extracted text to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Extracted text from {pdf_filename} to {output_file}")
        return output_file
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

def main():
    """
    Main function to extract text from all PDF files in the data directory.
    """
    # Default input directory for PDFs
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Set up directories
    pdf_dirs = [
        os.path.join(data_dir, "atrium_summary"),
        os.path.join(data_dir, "novant_summary"),
        os.path.join(data_dir, "atrium-exports", "all_import"),
        os.path.join(data_dir, "pdf_files")
    ]
    
    # Output directory for extracted text
    output_dir = os.path.join(data_dir, "extracted_text")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all PDF files in the specified directories
    processed_files = 0
    for pdf_dir in pdf_dirs:
        if os.path.exists(pdf_dir):
            pdf_files = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
            print(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
            
            for pdf_path in pdf_files:
                output_file = extract_text_from_pdf(pdf_path, output_dir)
                if output_file:
                    processed_files += 1
        else:
            print(f"Directory {pdf_dir} does not exist, skipping...")
    
    print(f"\nExtracted text from {processed_files} PDF files. Results stored in {output_dir}")

if __name__ == "__main__":
    main() 