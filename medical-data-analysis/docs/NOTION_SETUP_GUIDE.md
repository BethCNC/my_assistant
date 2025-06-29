# Medical Data to Notion Integration Setup Guide

This guide will walk you through setting up the integration between your medical data and Notion.

## Prerequisites

1. A Notion account
2. An OpenAI API key (for medical entity extraction)
3. Your medical documents in digital format (PDF, text, HTML, etc.)

## Step 1: Create a Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Give it a name (e.g., "Medical Data Integration")
4. Select your workspace
5. Set the following capabilities:
   - Read content
   - Update content
   - Insert content
6. Click "Submit" to create the integration
7. Copy your "Internal Integration Token" (starts with `secret_`)

## Step 2: Create Databases in Notion

You'll need to create the following databases:

### 1. Medical Calendar Database

Create a database with these properties:
- Name (title property)
- Date (date property)
- Doctor (relation to Medical Team)
- Type (select property)
- Status (select property)
- Notes (text property)
- Location (text property)
- Symptoms (relation to Symptoms)
- Conditions (relation to Medical Conditions)
- Attachments (files property)

### 2. Medical Team Database

Create a database with these properties:
- Name (title property)
- Specialty (select property)
- Contact (text property)
- Office (text property)
- First Visit (date property)
- Appointments (relation to Medical Calendar)
- Notes (text property)
- Status (select property)
- Conditions (relation to Medical Conditions)
- id (text property)

### 3. Medical Conditions Database

Create a database with these properties:
- Name (title property)
- Status (select property)
- Date Diagnosed (date property)
- Diagnosing Doctor (relation to Medical Team)
- Treating Doctors (relation to Medical Team)
- Symptoms (relation to Symptoms)
- Medications (relation to Medications)
- Related Appointments (relation to Medical Calendar)
- Notes (text property)
- ICD-10 Code (text property)
- Category (select property)

### 4. Medications Database

Create a database with these properties:
- Name (title property)
- Generic Name (text property)
- Dosage (text property)
- Start Date (date property)
- End Date (date property)
- Status (select property)
- For Condition (relation to Medical Conditions)
- Prescribed By (relation to Medical Team)
- Side Effects (text property)
- Notes (text property)
- Effectiveness (select property)

### 5. Symptoms Database

Create a database with these properties:
- Name (title property)
- First Observed (date property)
- Status (select property)
- Severity (select property)
- Frequency (select property)
- Related Condition (relation to Medical Conditions)
- Related Medication (relation to Medications)
- Daily Impact (text property)
- Notes (text property)
- Triggers (text property)

## Step 3: Share Databases with Your Integration

For each database you've created:
1. Open the database
2. Click "Share" in the top right
3. Click "Add people, groups, or integrations"
4. Search for your integration by name
5. Click "Invite"

## Step 4: Get Database IDs

For each database, get its ID from the URL:
1. Open the database in full page view
2. Copy the part of the URL after the last slash and before any query parameters
   - Example: in `https://www.notion.so/myworkspace/83452aab12345b12ab6576c99abab432`, the ID is `83452aab12345b12ab6576c99abab432`

## Step 5: Configure the Integration

1. Edit the `config/notion_config.json` file with:
   - Your OpenAI API key
   - Your Notion integration token
   - Your database IDs

```json
{
  "openai": {
    "api_key": "your_openai_api_key_here",
    "model": "gpt-4o",
    "temperature": 0.1
  },
  "notion": {
    "token": "your_notion_api_token_here",
    "databases": {
      "medical_calendar": "your_medical_calendar_database_id_here",
      "medical_team": "your_medical_team_database_id_here",
      "medical_conditions": "your_medical_conditions_database_id_here",
      "medications": "your_medications_database_id_here",
      "symptoms": "your_symptoms_database_id_here"
    }
  }
}
```

## Step 6: Prepare Your Medical Data

1. Place your medical documents in the `data/input` directory
2. Supported formats are: PDF, text, HTML, DOCX, Markdown, RTF, and CSV

## Step 7: Run the Integration

1. Run the integration script:
   ```
   ./run_notion_sync.sh
   ```

2. The script will:
   - Process all your medical documents
   - Extract entities like appointments, conditions, medications, etc.
   - Create entries in your Notion databases
   - Link related entities together

## Troubleshooting

- If you encounter API errors, check your API tokens
- If properties aren't being properly filled, ensure your database structure matches the expected schema
- For extraction issues, try adjusting the model parameters in your config file
- Check the log files in the logs directory for detailed error information

## Next Steps

- Add more documents to the input directory and re-run the sync
- Customize the extraction prompts in `src/notion_integration/extraction_prompts.py` for your specific needs
- Adjust the schema mapping in `src/notion_integration/notion_database_schema.py` if you've customized your database structure 