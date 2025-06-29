# Therapist Data Import Guide

This guide explains how to use the scripts to extract therapist information from various counseling websites and import them into your Notion database.

## Setup

1. Ensure your `.env` file contains the Notion API token:
   ```
   NOTION_TOKEN=your_notion_integration_token_here
   ```

2. Make sure the Notion integration has been added to your "Therapist Options" database in Notion.

3. Install the required dependencies:
   ```bash
   npm install
   ```

## Scripts Overview

### 1. Check Therapist Database

This script verifies that the Notion database exists and that your integration has proper access to it:

```bash
npm run check-therapist-db
```

This will:
- Test the connection to your Notion database
- Display the database properties
- Show some existing entries (if any)

If this script fails, you'll need to fix your integration permissions or database ID before proceeding.

### 2. Import Therapists

This script extracts therapist information from the websites specified in the `therapist-rules.mdc` file and adds them to your Notion database:

```bash
npm run import-therapists
```

The script will:
1. Scrape data from all target websites
2. Extract therapist names, bios, locations, and other relevant information
3. Create new entries in your Notion database
4. Set default values for "Mom" and "Final Vote" status fields to "Unknown"

## Target Websites

The following websites are targeted for data extraction:

1. Glenda Vinson Nnaji - Psychology Today
2. Reaching Resolution
3. Myriam Rabaste - NeuroNNection
4. Thrive Counseling
5. Anna Thames Counseling

## Notion Database Fields

The script populates these fields in your Notion database:

1. **Name**: Therapist's full name (Title field)
2. **Office/Group**: Practice affiliation (Multi-select field)
3. **Location**: Office location/address (Rich text field)
4. **Bio**: Complete therapist biography (Rich text field)
5. **Pros**: Automatically set to empty (Rich text field)
6. **Cons**: Automatically set to empty (Rich text field)
7. **Notes**: Additional observations such as specialties, education, etc. (Rich text field)
8. **Mom**: Set to "Unknown" (Status field)
9. **Final Vote**: Set to "Unknown" (Status field)

## Troubleshooting

### Permission Issues

If you encounter permission errors:
1. Make sure your Notion integration token is valid
2. Verify the integration has been added to the database
3. Check that the database ID is correct

### Data Extraction Problems

If the script fails to extract data from a website:
1. Check if the website structure has changed
2. Examine the scraping functions in `import-therapists-to-notion.js`
3. Update the CSS selectors to match the current website structure

### Rate Limiting

If you hit Notion API rate limits:
1. The script has built-in delays to avoid rate limiting
2. If needed, increase the delay between API calls in the script

## Manual Data Review

After running the import:
1. Review the imported data in Notion
2. Fill in any missing information
3. Update the "Pros", "Cons", and other subjective fields
4. Check for any duplicate entries

## Maintenance

The script may need periodic updates if:
1. Website structures change
2. New therapists are added to the practices
3. You want to add new target websites

To update the script, modify the extraction functions in `import-therapists-to-notion.js` accordingly. 