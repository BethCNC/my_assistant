import dotenv from 'dotenv';
import path from 'path';
import { Client } from '@notionhq/client';

// Load environment variables from .env.local and .env
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Notion client directly
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

console.log("Using Notion API token:", process.env.NOTION_TOKEN ? "Token found" : "Token not found");

async function checkNotionConnection() {
  try {
    console.log('Checking Notion connection and fetching databases...');
    
    // Try to get user information
    const user = await notion.users.me({});
    console.log('✅ Connected to Notion as:', user.name);
    
    // List all databases the user has access to
    const response = await notion.search({
      filter: {
        property: 'object',
        value: 'database'
      }
    });
    
    console.log(`\nFound ${response.results.length} databases:`);
    
    // Display information about each database
    for (const db of response.results) {
      if ('title' in db) {
        const titleArray = db.title || [];
        const title = titleArray.map((t: any) => t.plain_text || '').join('') || 'Untitled';
        console.log(`- Database: "${title}"`);
        console.log(`  ID: ${db.id}`);
        console.log(`  URL: ${db.url}`);
        console.log('');
      }
    }
    
    console.log('\nTo use these database IDs, update your .env.local file with the following values:');
    console.log('NOTION_MEDICAL_TEAM_DATABASE_ID=[medical team database id]');
    console.log('NOTION_DIAGNOSES_DATABASE_ID=[diagnoses database id]');
    console.log('NOTION_SYMPTOMS_DATABASE_ID=[symptoms database id]');
    console.log('NOTION_MEDICAL_CALENDAR_DATABASE_ID=[medical calendar database id]');
    
  } catch (error) {
    console.error('❌ Error connecting to Notion:', error);
    console.error('Error details:', error instanceof Error ? error.message : JSON.stringify(error));
  }
}

checkNotionConnection().catch(console.error); 