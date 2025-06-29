#!/usr/bin/env python3
# Extract PDF Lab Results
# Script to extract text from PDF lab results for further processing

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional, Union, Tuple
import tempfile

# Try to import PDF extraction libraries
try:
    import pdfplumber
    HAVE_PDFPLUMBER = True
except ImportError:
    HAVE_PDFPLUMBER = False

try:
    from pypdf import PdfReader
    HAVE_PYPDF = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        HAVE_PYPDF = True
    except ImportError:
        HAVE_PYPDF = False

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our lab results parser
try:
    from scripts.lab_results_parser import parse_lab_results
    from scripts.import_lab_results import process_lab_file
    HAVE_LAB_PARSER = True
except ImportError:
    HAVE_LAB_PARSER = False


def check_dependencies() -> None:
    """Check if required dependencies are installed"""
    missing = []
    
    if not HAVE_PDFPLUMBER and not HAVE_PYPDF:
        missing.append("pdfplumber or PyPDF2/pypdf")
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install required packages:")
        print("  pip install pdfplumber pypdf")
        sys.exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using available libraries
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    # Try pdfplumber first (better text extraction with layout preservation)
    if HAVE_PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n\n"  # Add page breaks
                
                if text.strip():  # If we got text, return it
                    return text
        except Exception as e:
            print(f"Warning: pdfplumber extraction failed: {e}")
    
    # Fall back to PyPDF2/pypdf
    if HAVE_PYPDF:
        try:
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                    text += "\n\n"  # Add page breaks
                return text
        except Exception as e:
            print(f"Warning: PyPDF extraction failed: {e}")
    
    # If we got here, both methods failed
    raise RuntimeError(f"Could not extract text from {pdf_path}")


def process_pdf(pdf_path: str, output_dir: Optional[str] = None, 
                extract_only: bool = False) -> Union[str, dict]:
    """
    Process a single PDF file to extract lab results
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted text and results
        extract_only: If True, only extract text without parsing
        
    Returns:
        Extracted text or parsed lab data
    """
    print(f"Processing {os.path.basename(pdf_path)}...")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Save extracted text if output directory specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(pdf_path)
        txt_filename = os.path.splitext(base_name)[0] + ".txt"
        txt_path = os.path.join(output_dir, txt_filename)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"  Saved extracted text to {txt_path}")
    
    # Return text only if requested
    if extract_only:
        return text
    
    # Parse lab results if parser is available
    if HAVE_LAB_PARSER:
        # Write to temporary file for processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
            temp_path = temp.name
            temp.write(text)
        
        try:
            # Process the text file with our lab results parser
            result = process_lab_file(temp_path, output_dir)
            
            # Delete temporary file
            os.unlink(temp_path)
            
            return result
        except Exception as e:
            # Delete temporary file in case of error
            os.unlink(temp_path)
            raise e
    else:
        return text


def process_directory(input_dir: str, output_dir: Optional[str] = None, 
                     extract_only: bool = False, recursive: bool = False) -> List[Union[str, dict]]:
    """
    Process all PDF files in a directory
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save extracted text and results
        extract_only: If True, only extract text without parsing
        recursive: Whether to search subdirectories
        
    Returns:
        List of extracted texts or parsed lab data
    """
    results = []
    
    # Get list of PDF files to process
    if recursive:
        pdf_paths = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_paths.append(os.path.join(root, file))
    else:
        pdf_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                    if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith('.pdf')]
    
    # Process each PDF file
    for pdf_path in pdf_paths:
        try:
            result = process_pdf(pdf_path, output_dir, extract_only)
            results.append(result)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
    
    print(f"Processed {len(results)} PDF files")
    return results


def main():
    """Main function to run when script is executed directly"""
    parser = argparse.ArgumentParser(description='Extract text from PDF lab results')
    parser.add_argument('input', help='Input PDF file or directory to process')
    parser.add_argument('--output-dir', '-o', help='Directory to save extracted text and results')
    parser.add_argument('--extract-only', '-e', action='store_true', 
                       help='Only extract text without parsing lab results')
    parser.add_argument('--recursive', '-r', action='store_true', 
                       help='Recursively process directories')
    
    args = parser.parse_args()
    
    # Check if required dependencies are installed
    check_dependencies()
    
    input_path = args.input
    
    if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        # Process single PDF file
        process_pdf(input_path, args.output_dir, args.extract_only)
    elif os.path.isdir(input_path):
        # Process directory of PDF files
        process_directory(input_path, args.output_dir, args.extract_only, args.recursive)
    else:
        print(f"Error: {input_path} is not a valid PDF file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main() 