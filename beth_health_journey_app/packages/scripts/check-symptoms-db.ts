import { Client } from '@notionhq/client';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env.local first
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const notionToken = process.env.NOTION_TOKEN;
const symptomsDbId = process.env.NOTION_SYMPTOMS_DATABASE_ID;

if (!notionToken || !symptomsDbId) {
  console.error('Missing required environment variables:');
  console.error('NOTION_TOKEN:', notionToken ? '✓' : '✗');
  console.error('NOTION_SYMPTOMS_DATABASE_ID:', symptomsDbId ? '✓' : '✗');
  process.exit(1);
}

console.log('Symptoms Database ID:', symptomsDbId);

const notion = new Client({ auth: notionToken });

async function checkSymptomsDatabase() {
  try {
    // Check if we can access the database
    const database = await notion.databases.retrieve({
      database_id: symptomsDbId as string
    });

    console.log('Successfully connected to database!');
    console.log('Database ID:', database.id);
    console.log('Object:', database.object);

    // Try to query the database
    const response = await notion.databases.query({
      database_id: symptomsDbId as string,
      page_size: 5
    });

    console.log('\nFound', response.results.length, 'symptoms');
    if (response.results.length > 0) {
      console.log('Sample entries:');
      response.results.forEach((page: any) => {
        console.log('-', page.properties?.Name?.title?.[0]?.plain_text || 'Untitled');
      });
    }

  } catch (error: any) {
    console.error('Error:', error?.message || 'Unknown error');
    process.exit(1);
  }
}

// Run the check
checkSymptomsDatabase().catch(console.error); 