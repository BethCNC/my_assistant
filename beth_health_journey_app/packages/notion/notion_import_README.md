# Medical Records Notion Import System

This system helps extract data from medical record PDFs and import them into Notion databases with consistent formatting.

## Overview

The system consists of two main Python scripts:

1. `import_helper.py` - Processes extracted text files and prepares them for Notion import
2. `notion_importer.py` - Imports the processed data into Notion using the Notion API

## Directory Structure

```
data/
├── extracted_text/        # Contains text files extracted from PDFs
├── atrium-exports/        # Original PDF files
│   └── all_import/        # PDFs organized by year
├── notion_import_ready/   # Output directory for processed entries
└── other directories...
```

## Data Verification

Before running the import process, we've verified:
- Each PDF in `data/atrium-exports/all_import` has corresponding text in `data/extracted_text`
- The text files contain properly extracted content from the PDFs
- A few extracted text files that are missing correspond to "Result Trends" PDFs which may be consolidated in other files

## Usage

### Step 1: Process Extracted Text

Run the `import_helper.py` script to analyze the extracted text files and prepare them for import:

```bash
python import_helper.py
```

This script:
- Reads all text files in `data/extracted_text/`
- Categorizes them by type (Lab Result, Doctor's Notes, Imaging Report, etc.)
- Extracts relevant information (date, doctor name, test results, etc.)
- Formats the data according to standardized rules for Notion import
- Saves the processed entries to `data/notion_import_ready/notion_ready_entries.json`

### Step 2: Import to Notion

Set your Notion API key as an environment variable:

```bash
export NOTION_API_KEY="your_notion_api_key_here"
```

Then run the Notion importer:

```bash
python notion_importer.py
```

This script:
- Reads the processed entries from `data/notion_import_ready/notion_ready_entries.json`
- Converts entries to Notion's API format
- Creates pages in the Medical Calendar database
- Formats content with proper headings, paragraphs, and lists
- Logs all activity to `data/notion_import_ready/import_log.txt`

## Data Standardization

The system standardizes medical record entries with consistent formatting:

### Lab Results
- Title format: `{Test Name} - {Date}`
- Content includes test name, normal ranges, and results

### Doctor's Notes
- Title format: `{Specialty} Visit - {Date}` (e.g., "GP Visit - 01/29/2025")
- Content includes patient info, chief complaint, and assessment/plan

### Imaging Reports
- Title format: `{Imaging Type} {Body Part} - {Date}` (e.g., "MRI Shoulder - 05/08/2018")
- Content includes the full radiology report or key findings

## Troubleshooting

If you encounter any issues:

1. Check the log file at `data/notion_import_ready/import_log.txt`
2. Verify your Notion API key has permission to access and modify the database
3. Ensure the database IDs in the scripts match your actual Notion databases

## Requirements

- Python 3.7+
- `requests` library
- Access to Notion API and appropriate permissions 