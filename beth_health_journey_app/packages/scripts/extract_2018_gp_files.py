#!/usr/bin/env python3
"""
Extract text from PDF files from the February 14, 2018 GP visit
and prepare them for import to Notion.
"""

import os
import re
import subprocess
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define directory paths
SOURCE_DIR = "data/atrium-exports/all_import/2018/GP/02_Feb 14 2018_Dr LiCause"
EXTRACTED_TEXT_DIR = "data/extracted_text"

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def clean_filename(filename):
    """
    Clean and standardize filename for the extracted text file.
    Format: MM_DD_YYYY_DoctorName_TestName.txt
    """
    # Extract test name from the original filename
    test_name = Path(filename).stem
    
    # Standardize filename
    return f"02_14_2018_DrLiCause_{test_name}.txt"

def extract_text_from_pdf(pdf_path, output_path):
    """
    Extract text from PDF file using pdftotext utility.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the extracted text
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Run pdftotext command
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, output_path],
            check=True,
            stderr=subprocess.PIPE
        )
        logger.info(f"Successfully extracted text from {pdf_path} to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {str(e)}")
        return False

def process_pdfs():
    """
    Process all PDF files in the source directory,
    extract text, and save to the extracted text directory.
    """
    # Ensure the output directory exists
    ensure_directory_exists(EXTRACTED_TEXT_DIR)
    
    # Get all PDF files in the source directory
    pdf_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {SOURCE_DIR}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(SOURCE_DIR, pdf_file)
        
        # Create standardized output filename
        output_filename = clean_filename(pdf_file)
        output_path = os.path.join(EXTRACTED_TEXT_DIR, output_filename)
        
        # Extract text from PDF
        success = extract_text_from_pdf(pdf_path, output_path)
        
        if success:
            # Verify extraction by checking file size
            if os.path.getsize(output_path) == 0:
                logger.warning(f"Extracted file is empty: {output_path}")
            else:
                logger.info(f"Successfully processed {pdf_file} -> {output_filename}")

def main():
    """Main function to extract text from PDF files."""
    logger.info("Starting PDF text extraction process...")
    process_pdfs()
    logger.info("PDF text extraction process completed")

if __name__ == "__main__":
    main() 