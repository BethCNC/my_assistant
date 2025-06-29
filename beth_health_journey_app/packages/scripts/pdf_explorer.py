#!/usr/bin/env python3
"""
PDF Explorer for Medical Records

A utility script to explore the structure of PDF files in a medical records directory.
Helps identify the structure and nature of PDFs before processing them in bulk.

Usage:
    python pdf_explorer.py --dir <directory_path>
"""

import os
import sys
import argparse
from pathlib import Path
import PyPDF2

def explore_pdf_directory(directory_path):
    """
    Explore a directory containing PDF files and report on its structure.
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Error: Directory {directory_path} does not exist")
        return
    
    print(f"Exploring directory: {directory_path}")
    
    # Get all PDF files recursively
    pdf_files = list(directory.glob('**/*.pdf'))
    
    if not pdf_files:
        print("No PDF files found in this directory.")
        return
    
    # Get directories containing PDFs
    pdf_dirs = set()
    for pdf in pdf_files:
        pdf_dirs.add(pdf.parent)
    
    # Basic counts
    total_pdfs = len(pdf_files)
    total_dirs = len(pdf_dirs)
    
    print(f"\nFound {total_pdfs} PDF files in {total_dirs} directories")
    
    # Analyze directory structure
    print("\nDirectory structure:")
    dir_structure = {}
    for pdf_dir in pdf_dirs:
        rel_path = str(pdf_dir.relative_to(directory))
        parts = rel_path.split(os.sep)
        
        current = dir_structure
        for part in parts:
            if part == '.':
                continue
            if part not in current:
                current[part] = {}
            current = current[part]
    
    # Print directory tree
    def print_dir_tree(tree, indent=0):
        for key, value in tree.items():
            print("  " * indent + f"- {key}/")
            print_dir_tree(value, indent + 1)
    
    print_dir_tree(dir_structure)
    
    # Count PDFs per directory
    print("\nPDFs per directory:")
    dir_counts = {}
    for pdf in pdf_files:
        rel_dir = str(pdf.parent.relative_to(directory))
        if rel_dir not in dir_counts:
            dir_counts[rel_dir] = 0
        dir_counts[rel_dir] += 1
    
    for dir_path, count in dir_counts.items():
        if dir_path == '.':
            dir_path = '(root)'
        print(f"  {dir_path}: {count} PDFs")
    
    # Sample a few PDFs to analyze structure
    print("\nSampling PDFs for structure analysis...")
    
    # Get up to 5 PDFs from each directory for a representative sample
    samples = []
    for dir_path in dir_counts.keys():
        if dir_path == '.':
            dir_pdfs = [pdf for pdf in pdf_files if pdf.parent == directory]
        else:
            dir_pdfs = [pdf for pdf in pdf_files if str(pdf.parent.relative_to(directory)) == dir_path]
        
        # Take up to 5 samples from this directory
        dir_samples = dir_pdfs[:min(5, len(dir_pdfs))]
        samples.extend(dir_samples)
    
    # Analyze the structure of sample PDFs
    print(f"\nAnalyzing {len(samples)} sample PDFs...")
    
    for i, pdf_path in enumerate(samples[:20]):  # Limit to 20 samples total
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                rel_path = str(pdf_path.relative_to(directory))
                print(f"\nSample {i+1}: {rel_path}")
                print(f"  Pages: {len(reader.pages)}")
                
                # Check metadata
                if reader.metadata:
                    print("  Metadata available:")
                    for key, value in reader.metadata.items():
                        if key and value:
                            # Clean up the key name
                            key_name = str(key)
                            if key_name.startswith('/'):
                                key_name = key_name[1:]
                            print(f"    {key_name}: {value}")
                else:
                    print("  No metadata available")
                
                # Try to extract first page text as a sample
                if len(reader.pages) > 0:
                    first_page = reader.pages[0]
                    text = first_page.extract_text()
                    if text:
                        # Limit sample to first 200 characters
                        sample_text = text[:200] + ('...' if len(text) > 200 else '')
                        print(f"  First page text sample: {sample_text}")
                    else:
                        print("  No extractable text found on first page")
                
        except Exception as e:
            print(f"  Error analyzing {pdf_path.name}: {str(e)}")
    
    print("\nPDF exploration complete.")

def main():
    parser = argparse.ArgumentParser(description="Explore PDF files in a directory")
    parser.add_argument("--dir", required=True, help="Directory path containing PDF files")
    args = parser.parse_args()
    
    explore_pdf_directory(args.dir)

if __name__ == "__main__":
    main()