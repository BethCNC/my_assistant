# Beth's Health Journey App

A personal application to track and organize my health information, medical history, and conditions in a structured format.

## Project Overview

This application helps organize medical records, lab results, and health information from multiple sources into a structured system to better track and manage multiple chronic illnesses.

## Features

- Medical timeline view
- Condition tracking
- Lab result organization
- Provider management
- Document storage and analysis
- PDF processing for medical records

## Tech Stack

- Next.js
- React
- TypeScript
- Supabase
- Notion API integration

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

## Scripts

- `process-medical-pdfs-to-notion.js`: Process medical PDFs and add them to Notion
- Various data import/export utilities for health data management

## Setup Instructions

### Prerequisites

- Node.js (v14 or later)
- npm (v7 or later)
- A Supabase account

### Step 1: Set up Supabase

1. Go to [Supabase](https://supabase.io/) and create a new project
2. Navigate to SQL Editor in your Supabase dashboard
3. Run the setup script which will generate instructions:
   ```bash
   npm run setup-db
   ```
4. Open `db/setup-instructions.md` and follow the steps to run the SQL in the Supabase SQL Editor

### Step 2: Configure Environment Variables

1. Copy your Supabase API keys from the Supabase dashboard:
   - Go to Project Settings > API
   - Copy the "Project URL" and "anon public" key
   - Copy the "service_role" key (keep this secure)

2. Update `.env.local` with your Supabase keys:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

3. Verify your Notion API keys and database IDs are correctly set in `.env.local`

### Step 3: Verify Database Connection

```bash
npm run check-db
```

### Step 4: Import Data from Notion to Supabase

```bash
npm run import-data
```

Or run individual imports if needed:
```bash
npx ts-node scripts/import-medical-team.ts
npx ts-node scripts/import-diagnoses.ts
npx ts-node scripts/import-symptoms.ts
npx ts-node scripts/import-medical-calendar.ts
```

## Health Data Integration

This app can integrate with multiple health data sources:

### Novant Health (Epic) Integration

For Novant Health, the app can directly import data from the Epic FHIR API:

1. Get a FHIR token from [fetch-my-epic-token.org](https://fetch-my-epic-token.org)
2. Update your token and import data:
   ```bash
   npx ts-node scripts/update-fhir-token.ts
   ```
3. Verify imported data:
   ```bash
   npx ts-node scripts/check-database.ts
   ```

### Atrium Health Integration

For Atrium Health, which doesn't offer direct FHIR API access to patients, use these tools:

1. For individual PDF exports:
   ```bash
   npx ts-node scripts/parse-atrium-pdfs.ts
   ```

2. To request a complete medical record:
   ```bash
   npx ts-node scripts/request-atrium-records.ts
   ```

3. Interactive guide for manual data extraction:
   ```bash
   npx ts-node scripts/extract-atrium-data.ts
   ```

See [Atrium Health Data Access Guide](docs/atrium-health-data-access.md) for detailed instructions.

## Running the Application

```bash
# Development mode
npm run dev

# Build for production
npm run build

# Run production version
npm start
```

## Storybook Component Library

This project uses Storybook to develop and showcase UI components:

```bash
# Start Storybook development server
npm run storybook

# Build static Storybook site
npm run build-storybook
```

## Project Structure

- `/components` - React components
  - `/layout` - Layout components (header, footer, etc.)
  - `/ui` - UI components (buttons, cards, etc.)
  - `/diagnoses` - Diagnosis-related components
  - `/symptoms` - Symptom-related components
  - `/medical-team` - Medical team components
  
- `/db` - Database schema and migrations

- `/docs` - Documentation files
  - `atrium-health-data-access.md` - Guide for Atrium Health data access

- `/lib` - Utility code
  - `/notion` - Notion API client
  - `/supabase` - Supabase client and types

- `/pages` - Next.js page components
  - `/api` - API routes

- `/scripts` - Data import and processing scripts
  - `check-database.ts` - Verify imported data
  - `import-from-epic.ts` - Epic FHIR API importer
  - `update-fhir-token.ts` - Update Epic FHIR tokens
  - `parse-atrium-pdfs.ts` - Organize Atrium Health PDF exports
  - `request-atrium-records.ts` - Generate medical record request
  - `extract-atrium-data.ts` - Guide for manual data extraction

- `/styles` - CSS and design tokens

## Further Development

1. Complete the UI implementation following your design system
2. Implement authentication if needed
3. Set up recurring data synchronization from Notion to Supabase
4. Add data visualization for medical timelines and lab results
5. Develop PDF parsers for imported Atrium Health records
6. Implement a CCD/CDA parser for standardized health records

# Health Journey App

Personal health journey tracker and medical data management system that processes medical PDFs and integrates with Notion and Supabase.

## Features

- Extract text from medical PDFs (lab results, appointment notes, etc.)
- Use AI to analyze and categorize medical content
- Sync data with Notion databases
- Store structured data in Supabase
- Import healthcare providers from CSV

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file with the following variables:
   ```
   # Supabase
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   ```

## PDF Processing Pipeline

This script extracts text from PDFs in your medical folder structure, uses AI to analyze the content, and adds it to both Notion and Supabase.

### Directory Structure

The script expects PDFs to be organized in the following structure:
```
data/atrium-exports/all_import/
  ├── 2023/
  │   ├── Endocrinology/
  │   │   └── 06_June 15 2023 - Dr Gagneet/
  │   │       ├── TSH.pdf
  │   │       ├── Vitamin d, 25 - Hydroxy.pdf
  │   │       └── ...
  │   ├── Eye/
  │   │   └── ...
  │   └── ...
  ├── 2022/
  │   └── ...
  └── ...
```

### Running the Script

```
npm run process-pdfs [start_year] [end_year]
```

- `start_year`: Optional. Year to start processing from (default: 2018)
- `end_year`: Optional. Year to end processing at (default: 2025)

Example:
```
npm run process-pdfs 2022 2023
```

## Provider Import

This script imports healthcare providers from a CSV file into both Notion and Supabase.

### CSV Format

The script expects a CSV file named `medical_team.csv` with the following columns:
```
Name,Specialty,Facility,Start Date,Conditions,Address,Phone,Email,Website,...,Notes,Status
```

Example row:
```
"Dr. Gagneet Chauhan","Endocrinologist","Atrium Health - Endocrinology SouthPark","July 2023","Hashimoto's Thyroiditis,PCOS","4525 Cameron Valley Parkway 4th Floor, Charlotte, NC 28211","704-468-8876","","","","","Previous Provider"
```

### Running the Script

```
npm run import-providers
```

## Using with MCP Server

Both scripts are designed to work with the Notion MCP server integration. When run within the MCP environment, they will automatically use the MCP Notion functions.

If run outside of the MCP environment, they will use mock functions for testing, which simply log actions without making actual API calls to Notion.

## Customization

### Supabase Setup

Make sure your Supabase database has the following tables:
- `providers` - Healthcare providers
- `medical_events` - Medical appointments, procedures, etc.
- `lab_results` - Laboratory test results
- `conditions` - Medical conditions/diagnoses

### Notion Setup

Update the Notion database IDs in the scripts to match your databases:
```javascript
const NOTION_MEDICAL_CALENDAR_DB = 'your-calendar-db-id';
const NOTION_MEDICAL_TEAM_DB = 'your-providers-db-id';
const NOTION_CONDITIONS_DB = 'your-conditions-db-id';
```

## Troubleshooting

### PDF Text Extraction

The script attempts to use multiple methods for extracting text:
1. `pdftotext` command-line tool (if available)
2. macOS `textutil` command (for macOS systems)

If neither works, you may need to install additional tools:
- On macOS: `brew install poppler` (for pdftotext)
- On Ubuntu: `apt-get install poppler-utils`

### Notion API Errors

If encountering Notion API errors, check:
- Database IDs are correct
- Database schema matches expected properties
- You have proper access permissions

### Supabase Errors

If encountering Supabase errors, check:
- Connection URL and API key are correct
- Database schema matches expected table structure
- RLS policies allow the service key to perform operations

