import { Client } from '@notionhq/client';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const notionToken = process.env.NOTION_TOKEN;

if (!notionToken) {
  console.error('NOTION_TOKEN not found in environment variables');
  process.exit(1);
}

const notion = new Client({
  auth: notionToken,
});

async function listDatabases() {
  try {
    const response = await notion.search({
      filter: {
        property: 'object',
        value: 'database'
      }
    });
    
    console.log('\nAccessible Databases:');
    response.results.forEach((db: any) => {
      console.log(`\nID: ${db.id}`);
      console.log(`Title: ${db.title[0]?.plain_text || 'Untitled'}`);
      console.log(`URL: ${db.url}`);
    });
    
    console.log(`\nTotal databases found: ${response.results.length}`);
  } catch (error: any) {
    console.error('Failed to list databases!');
    console.error('Error:', error.message);
    if (error.code) console.error('Error code:', error.code);
    if (error.status) console.error('Status:', error.status);
  }
}

listDatabases(); 