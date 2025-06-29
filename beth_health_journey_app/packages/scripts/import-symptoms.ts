import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import { Client } from '@notionhq/client';
import type { Database } from '../lib/supabase/database.types';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_API_KEY || process.env.NOTION_TOKEN,
});

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient<Database>(supabaseUrl, supabaseServiceKey);

// Notion database ID for symptoms
const SYMPTOMS_DATABASE_ID = process.env.NOTION_SYMPTOMS_DATABASE_ID || '17b86edc-ae2c-81c6-9077-e55a68cf2438';

async function importSymptoms() {
  try {
    console.log('Using Notion API token:', process.env.NOTION_TOKEN ? 'Token found' : 'No token found');
    console.log('Fetching symptoms from Notion...');
    console.log(`Using database ID: ${SYMPTOMS_DATABASE_ID}`);
    
    // Check if the database exists first
    try {
      await notion.databases.retrieve({ database_id: SYMPTOMS_DATABASE_ID });
    } catch (error) {
      console.error(`Error: Could not retrieve symptoms database with ID ${SYMPTOMS_DATABASE_ID}.`);
      console.error('Please check your NOTION_SYMPTOMS_DATABASE_ID in .env.local');
      process.exit(1);
    }
    
    const response = await notion.databases.query({
      database_id: SYMPTOMS_DATABASE_ID,
    });

    console.log(`Found ${response.results.length} symptoms`);

    for (const page of response.results) {
      // Handle the different types of page responses safely
      if (!('properties' in page)) {
        console.warn(`Skipping page ${page.id} - properties not found`);
        continue;
      }
      
      const properties = page.properties as Record<string, any>;
      
      // Extract symptom data from Notion properties
      const symptom = {
        id: page.id,
        name: properties.Name?.title?.[0]?.plain_text || 'Unnamed Symptom',
        description: properties.Description?.rich_text?.[0]?.plain_text || '',
        severity: properties.Severity?.number || null,
        frequency: properties.Frequency?.rich_text?.[0]?.plain_text || '',
        duration: properties.Duration?.rich_text?.[0]?.plain_text || '',
        triggers: properties.Triggers?.multi_select?.map((t: any) => t.name) || [],
        alleviating_factors: properties['Alleviating Factors']?.multi_select?.map((f: any) => f.name) || [],
        date_recorded: properties['Date Recorded']?.date?.start || new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      console.log(`Importing symptom: ${symptom.name}`);

      // Insert into Supabase
      const { data, error } = await supabase
        .from('symptoms')
        .upsert([symptom], {
          onConflict: 'id'
        });

      if (error) {
        console.error(`Error importing symptom ${symptom.name}:`, error);
      } else {
        console.log(`Successfully imported symptom: ${symptom.name}`);
      }
    }

    console.log('Symptom import completed!');

  } catch (error) {
    console.error('Error importing symptoms:', error);
    process.exit(1);
  }
}

// Run the import
importSymptoms().catch(console.error); 