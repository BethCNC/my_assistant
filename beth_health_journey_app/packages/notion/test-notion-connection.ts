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

console.log('Token found:', notionToken.substring(0, 4) + '...');

const notion = new Client({
  auth: notionToken,
});

async function testConnection() {
  try {
    // Try to list users (one of the simplest API calls)
    const response = await notion.users.list({});
    console.log('Connection successful!');
    console.log('Bot user:', response.results[0]);
  } catch (error: any) {
    console.error('Connection failed!');
    console.error('Error status:', error.status);
    console.error('Error code:', error.code);
    console.error('Error message:', error.message);
    console.error('Request ID:', error.requestId);
  }
}

testConnection(); 