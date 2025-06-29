# Notion Medical Data Integration

This README explains how to use the Notion integration pipeline for your medical data project.

## Setup

1. Create a `.env` file in the project root with your Notion API token:
   ```
   NOTION_TOKEN=your_notion_api_token_here
   ```

2. Ensure the `config/notion_config.json` file contains the correct Notion database IDs:
   ```json
   {
     "notion": {
       "token": "NOTION_API_TOKEN_GOES_HERE",
       "databases": {
         "medical_calendar": "17b86edc-ae2c-81c1-83e0-e0a19a035932",
         "medical_team": "17b86edc-ae2c-8155-8caa-fbb80647f6a9",
         "medical_conditions": "17b86edc-ae2c-8167-ba15-f9f03b49795e",
         "medications": "17b86edc-ae2c-81a7-b28a-e9fbcc7e7b62",
         "symptoms": "17b86edc-ae2c-81c6-9077-e55a68cf2438"
       },
       "api_version": "2022-06-28"
     }
   }
   ```

3. Verify the field mapping in `config/notion_field_mapping.json` matches your Notion database structure.

## Running the Pipeline

### Full Pipeline

To run the complete pipeline, which extracts, formats, and imports medical data to Notion:

```bash
python run_notion_pipeline.py
```

### Options

```
--input-dir DIR       Directory with processed medical data (default: processed_data)
--output-dir DIR      Output directory for formatted data (default: data)
--config-dir DIR      Configuration directory (default: config)
--max-events N        Maximum number of events to process (0 = no limit)
--dry-run             Process data but don't import to Notion
```

### Individual Steps

If you need to run only specific parts of the pipeline:

1. **Extract Data**:
   ```bash
   python scripts/extract_medical_data.py --input-dir=processed_data --output-file=data/medical_events.json
   ```

2. **Format Data**:
   ```bash
   python scripts/format_for_notion.py --input-file=data/medical_events.json --output-file=data/notion_formatted_events.json --field-mapping=config/notion_field_mapping.json
   ```

3. **Import to Notion**:
   ```bash
   python scripts/import_to_notion.py --input-file=data/notion_formatted_events.json --config-file=config/notion_config.json
   ```

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Verify your Notion token is correct in the `.env` file
2. Check that your integration has access to the databases in the Notion workspace
3. Ensure your token has not expired (Notion tokens are valid for 1 year)

### Import Errors

If events fail to import:

1. Check the error message for field type mismatches
2. Make sure all required properties are included in the formatted events
3. Verify the database structure in Notion matches the field mapping

### Common Issues

#### Field Type Mismatches

If you encounter errors like: "Field X is expected to be Y" during import, this indicates a mismatch between how the formatter is treating fields and the actual field types in your Notion database.

Common field type issues:
- **Salt Tabs**: Should be formatted as a number field, not a checkbox
- **Glows/Grows**: Should be formatted as rich_text fields, not multi-select
- **Notes**: Is a relation field in the database, not a rich_text field

If you encounter similar issues with other fields, check your database structure using the test script:

```bash
python scripts/test_notion_connection.py --verbose
```

Then update the field handling in `scripts/format_for_notion.py` accordingly.

### Database Schema

The integration expects the following fields in the medical calendar database:

- Name (title)
- Date (date)
- Type (select)
- Purpose (rich_text)
- Doctor (relation to Medical Team database)
- Related Diagnoses (relation to Medical Conditions database)
- Linked Symptoms (relation to Symptoms database)
- Medications (relation to Medications database)

## Sample Data

The pipeline includes a sample medical events file (`data/medical_events.json`) that you can use for testing.

## Extending the Integration

To add support for additional Notion databases or field types:

1. Update the `notion_config.json` file with the new database IDs
2. Add appropriate field mappings in `notion_field_mapping.json`
3. Extend the `NotionMedicalClient` class in `src/notion_integration/notion_client.py` as needed
4. Create formatters for new field types in `src/notion_integration/formatters.py`

## Limitations

- The current implementation supports only basic Notion field types
- Complex relations between multiple databases may require manual handling
- Rate limiting can affect large imports (default: 3 requests per second)
- Some field types (like formulas and rollups) cannot be directly set through the API 