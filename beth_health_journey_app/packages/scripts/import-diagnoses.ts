import dotenv from 'dotenv';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import { Client } from '@notionhq/client';
import type { Database } from '../lib/supabase/database.types';

// Load environment variables from .env.local and .env
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Notion client directly
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

console.log("Using Notion API token:", process.env.NOTION_TOKEN ? "Token found" : "Token not found");

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string;
const supabase = createClient<Database>(supabaseUrl, supabaseServiceKey);

// Notion database ID for diagnoses
const DIAGNOSES_DATABASE_ID = process.env.NOTION_DIAGNOSES_DATABASE_ID;

// Helper function to safely extract values from Notion properties
function getPropertyValue(property: any): any {
  if (!property) return null;
  
  try {
    // Handle different property types
    switch(property.type) {
      case 'title':
        return property.title?.[0]?.plain_text || null;
      case 'rich_text':
        return property.rich_text?.[0]?.plain_text || null;
      case 'select':
        return property.select?.name || null;
      case 'multi_select':
        return property.multi_select?.map((item: any) => item.name) || [];
      case 'phone_number':
        return property.phone_number || null;
      case 'email':
        return property.email || null;
      case 'url':
        return property.url || null;
      case 'date':
        return property.date?.start || null;
      case 'checkbox':
        return property.checkbox || null;
      case 'number':
        return property.number || null;
      case 'relation':
        return property.relation?.[0]?.id || null;
      default:
        return null;
    }
  } catch (error) {
    console.error(`Error extracting property value:`, error);
    return null;
  }
}

async function importDiagnoses() {
  if (!DIAGNOSES_DATABASE_ID) {
    console.error('Missing NOTION_DIAGNOSES_DATABASE_ID environment variable');
    process.exit(1);
  }

  try {
    // Fetch diagnoses from Notion
    console.log('Fetching diagnoses from Notion...');
    console.log(`Using database ID: ${DIAGNOSES_DATABASE_ID}`);
    
    const response = await notion.databases.query({
      database_id: DIAGNOSES_DATABASE_ID as string,
    });

    const diagnoses = response.results;
    console.log(`Found ${diagnoses.length} diagnoses in Notion.`);

    // Process each diagnosis and insert into Supabase
    for (const diagnosis of diagnoses) {
      console.log(`Processing diagnosis with ID: ${diagnosis.id}`);
      
      // Safely access properties
      if (!('properties' in diagnosis)) {
        console.error(`Diagnosis ${diagnosis.id} doesn't have properties field`);
        continue;
      }
      
      const properties = diagnosis.properties;
      
      // Safely extract diagnosis information
      const conditionData = {
        name: getPropertyValue(properties.Name) || 'Unnamed Condition',
        description: getPropertyValue(properties.Description),
        date_diagnosed: getPropertyValue(properties['Date Diagnosed']),
        status: getPropertyValue(properties.Status)?.toLowerCase(),
        severity: getPropertyValue(properties.Severity),
        category: getPropertyValue(properties.Category),
        notes: getPropertyValue(properties.Notes),
        provider_id: null, // We'll need to match this with providers we created
      };

      console.log(`Importing diagnosis: ${conditionData.name}`);
      
      // Insert into Supabase
      const { data, error } = await supabase
        .from('conditions')
        .insert([conditionData])
        .select();

      if (error) {
        console.error(`Error importing diagnosis ${conditionData.name}:`, error);
      } else if (data && data.length > 0) {
        console.log(`Successfully imported diagnosis: ${conditionData.name}`);
      }
    }

    console.log('Import complete!');

  } catch (error) {
    console.error('❌ Error importing diagnoses:', error);
    console.error('Error details:', error instanceof Error ? error.message : JSON.stringify(error));
    process.exit(1);
  }
}

// Run the import
importDiagnoses().catch(console.error); 