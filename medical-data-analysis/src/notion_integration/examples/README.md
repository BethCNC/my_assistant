# Medical Data to Notion Examples

This directory contains example scripts showing how to use the Medical Data to Notion integration.

## Basic Usage Example

The basic workflow for integrating medical data with Notion is:

1. Create a configuration file with your Notion API token and database IDs
2. Initialize the `MedicalDataProcessor` with the configuration
3. Process medical documents with the processor
4. Review the results in your Notion databases

## Running the Examples

Before running any examples, make sure to:

1. Install the required dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Create a `notion_config.json` file with your Notion API token and database IDs:
   ```json
   {
     "notion": {
       "token": "your_notion_api_token",
       "databases": {
         "medical_calendar": "your_medical_calendar_database_id",
         "medical_team": "your_medical_team_database_id",
         "medical_conditions": "your_medical_conditions_database_id",
         "medications": "your_medications_database_id",
         "symptoms": "your_symptoms_database_id"
       }
     },
     "openai": {
       "api_key": "your_openai_api_key",
       "model": "gpt-4o",
       "temperature": 0.1
     }
   }
   ```

3. Run an example:
   ```bash
   python simple_example.py
   ```

## Example Scripts

- `simple_example.py`: Demonstrates basic usage of the integration
- `batch_processing.py`: Shows how to process multiple files in batch
- `csv_import.py`: Example of importing medical data from CSV files
- `pdf_processing.py`: Example of extracting data from PDF documents

## Customizing the Integration

To customize the integration for your specific needs:

1. Modify the schema mapping in `notion_database_schema.py`
2. Create custom extraction prompts in `extraction_prompts.py`
3. Extend the `EntityExtractor` class with specialized extraction methods
4. Update the property mappings to match your Notion database structure

## Troubleshooting

- If you encounter errors with the Notion API, check that your API token has the necessary permissions
- For LLM extraction issues, try adjusting the temperature or providing more context
- Make sure your Notion database IDs are correct and the databases have the expected properties 