#!/bin/bash

# Medical Records Processing Pipeline
# This script runs all three Python scripts in sequence to process medical records:
# 1. Extract text from PDFs
# 2. Analyze the extracted text
# 3. Prepare data for Notion import

echo "=== Starting Medical Records Processing Pipeline ==="

# Create directories if they don't exist
mkdir -p data/extracted_text
mkdir -p data/analysis_results
mkdir -p data/notion_import

# Step 1: Extract text from PDFs
echo "Step 1: Extracting text from PDF files..."
python3 scripts/extract_pdf_text.py
echo "Text extraction complete."
echo

# Step 2: Analyze the extracted text
echo "Step 2: Analyzing extracted text..."
python3 scripts/analyze_medical_text.py
echo "Text analysis complete."
echo

# Step 3: Prepare data for Notion import
echo "Step 3: Preparing data for Notion import..."
python3 scripts/prepare_notion_import.py
echo "Notion import preparation complete."
echo

echo "=== Medical Records Processing Pipeline Completed ==="
echo "Results are available in:"
echo "- Extracted text: data/extracted_text"
echo "- Analysis results: data/analysis_results.json"
echo "- Notion import files: data/notion_import" 