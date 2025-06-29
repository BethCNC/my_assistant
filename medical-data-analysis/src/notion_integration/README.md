# Medical Data to Notion Integration

A Python package for extracting structured medical data from documents and syncing it to Notion databases.

## Overview

This package provides tools to:

1. Process various medical document formats (PDF, text, HTML, etc.)
2. Extract medical entities (appointments, doctors, diagnoses, symptoms, medications)
3. Structure the data into a standardized format
4. Sync the data to Notion databases
5. Maintain relationships between medical entities

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/medical_data.git
cd medical_data

# Install the package
pip install -e ./src/notion_integration
```

Alternatively, install dependencies directly:

```bash
pip install -r src/notion_integration/requirements.txt
```

## Configuration

Create a configuration file (e.g., `notion_config.json`) with your Notion and OpenAI API keys:

```json
{
  "notion": {
    "token": "your_notion_api_token_here",
    "databases": {
      "medical_calendar": "medical_calendar_database_id_here",
      "medical_team": "medical_team_database_id_here",
      "medical_conditions": "medical_conditions_database_id_here",
      "symptoms": "symptoms_database_id_here",
      "medications": "medications_database_id_here"
    }
  },
  "openai": {
    "api_key": "your_openai_api_key_here",
    "model": "gpt-4o",
    "temperature": 0.1
  },
  "extraction": {
    "chunk_size": 4000,
    "chunk_overlap": 200,
    "default_document_type": "medical_document"
  },
  "processing": {
    "default_extensions": [".pdf", ".txt", ".html", ".docx", ".rtf", ".csv", ".md"],
    "max_workers": 2
  }
}
```

## Usage

### Command-line Interface

Process a single medical document:

```bash
python -m notion_integration.notion_data_syncer --config notion_config.json --doc path/to/document.pdf
```

Process all medical documents in a directory:

```bash
python -m notion_integration.notion_data_syncer --config notion_config.json --dir path/to/documents/ --recursive
```

### Python API

```python
from notion_integration.medical_data_processor import MedicalDataProcessor

# Initialize the processor with your config
processor = MedicalDataProcessor(config_path="path/to/config.json")

# Process a document and extract medical entities
extracted_data = processor.process_document("path/to/document.pdf")

# Sync the extracted data to Notion
results = processor.create_notion_entries(extracted_data)

print(f"Created {results['created']['appointments']} appointments")
print(f"Created {results['created']['doctors']} doctors")
print(f"Created {results['created']['diagnoses']} diagnoses")
```

## Examples

Check the `examples/` directory for more detailed examples:

- `simple_example.py`: Basic usage of the MedicalDataProcessor
- `batch_processing.py`: Process multiple documents in batch
- `pdf_processing.py`: Extract medical data from PDF documents
- `end_to_end_example.py`: Complete workflow from document processing to Notion sync

To run the end-to-end example:

```bash
# First create a config file
python src/notion_integration/examples/end_to_end_example.py --create-config --config my_config.json

# Edit the config file with your API keys and database IDs

# Then run the example with your config
python src/notion_integration/examples/end_to_end_example.py --config my_config.json
```

## Core Components

- **MedicalDataProcessor**: Main class that orchestrates the extraction and sync process
- **EntityExtractor**: Extracts medical entities from text using LLMs and custom NER
- **DocumentProcessor**: Processes various document formats into text
- **NotionIntegration**: Handles communication with the Notion API
- **NotionEntityMapper**: Maps extracted entities to Notion database properties
- **NotionDatabaseSchema**: Defines the structure of Notion databases

## License

MIT License 