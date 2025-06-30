#!/usr/bin/env python
"""
Command-line script to run the medical data ingestion pipeline.

This script provides a simple interface to process medical documents through
the end-to-end data ingestion pipeline.

Usage:
    python run_ingestion_pipeline.py path/to/input [options]

Example:
    # Process a single file
    python run_ingestion_pipeline.py samples/medical_note_sample.txt
    
    # Process all files in a directory
    python run_ingestion_pipeline.py samples
    
    # Process without using AI models (fallback to rule-based)
    python run_ingestion_pipeline.py samples --no-models
    
    # Process without storing in database
    python run_ingestion_pipeline.py samples --no-db
"""

import sys
from src.pipeline.ingestion_pipeline import main

if __name__ == "__main__":
    sys.exit(main()) 