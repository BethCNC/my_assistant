# Medical Data Processing System

A comprehensive system for processing medical documents, extracting structured entities, and syncing to Notion databases.

## Features

- Extract medical entities from various document formats (text, HTML, PDF)
- Process appointment notes, medications, diagnoses, symptoms, and provider information
- Map extracted entities to structured Notion databases
- Maintain chronological medical timelines
- Perform semantic search using medical entity embeddings

## Project Structure

```
medical_data/
├── config/                     # Configuration files
│   ├── notion_config.json      # Notion database configuration
│   └── notion_field_mapping.json  # Field mapping for Notion integration
├── data/                       # Data directory
│   ├── input/                  # Input medical documents
│   └── processed_data/         # Processed data output
├── src/                        # Source code
│   └── notion_integration/     # Notion integration components
│       ├── document_processor.py     # Document extraction
│       ├── entity_extractor.py       # Medical entity extraction
│       ├── extraction_prompts.py     # LLM prompts for entity extraction
│       ├── medical_data_processor.py # Main processor
│       ├── notion_client.py          # Notion API client
│       └── notion_entity_mapper.py   # Maps entities to Notion properties
├── check_env.py                # Environment validation
├── set_notion_token.py         # Script to set Notion API token
├── sync_medical_data.py        # Run the medical data sync process
├── sync_to_notion.py           # Sync extracted entities to Notion
├── test_extraction.py          # Test entity extraction
├── test_notion_integration.py  # Test Notion integration
└── run_test_extraction.py      # Extract entities from sample data
```

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key for entity extraction
- Notion API key for syncing to Notion databases
- Notion databases created according to the configuration

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/medical_data.git
   cd medical_data
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file to include your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   NOTION_TOKEN=your_notion_api_token
   ```

5. Configure Notion databases:
   - Create databases in Notion for appointments, medications, diagnoses, symptoms, and providers
   - Update `config/notion_config.json` with your database IDs
   - Adjust `config/notion_field_mapping.json` to match your database properties

## Usage

### Extract Medical Entities

```bash
python test_extraction.py data/input/your_medical_document.txt
```

### Test Notion Integration

```bash
python test_notion_integration.py
```

### Sync Medical Data to Notion

```bash
python sync_to_notion.py data/input/your_medical_document.txt
```

### Process a Batch of Documents

```bash
python sync_medical_data.py --input-dir data/input --output-dir data/processed_data
```

## Data Flow

1. **Document Processing**: Raw medical documents are parsed into plain text
2. **Entity Extraction**: LLM extracts structured entities from document text
3. **Entity Mapping**: Extracted entities are mapped to Notion properties
4. **Notion Sync**: Entities are synced to respective Notion databases

## Notion Database Structure

The system is designed to work with the following Notion databases:

- **Appointments**: Medical appointments and visits
- **Medications**: Prescribed and OTC medications
- **Diagnoses**: Medical diagnoses and conditions
- **Symptoms**: Reported symptoms and their severity
- **Providers**: Healthcare providers and facilities

## Extending the System

### Adding New Entity Types

1. Add the new entity type to `extraction_prompts.py`
2. Update `notion_field_mapping.json` with the new entity type
3. Create a Notion database for the new entity
4. Add the database ID to `notion_config.json`

### Supporting New Document Formats

1. Enhance `document_processor.py` to handle the new format
2. Add a new extraction method for the specific format
3. Update the MIME type detection if necessary

## License

[MIT License](LICENSE)

## Acknowledgments

- This project uses OpenAI's LLM for entity extraction
- Notion API for database integration 