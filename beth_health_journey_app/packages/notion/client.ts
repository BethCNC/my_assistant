import { Client } from '@notionhq/client';

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_API_KEY || process.env.NOTION_TOKEN, // Try both environment variables
});

export default notion; 