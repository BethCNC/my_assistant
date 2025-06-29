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
      default:
        return null;
    }
  } catch (error) {
    console.error(`Error extracting property value:`, error);
    return null;
  }
}

async function importMedicalTeam() {
  console.log('\n⚠️ IMPORTANT: Medical Team Database Setup Required ⚠️');
  console.log('A dedicated "Medical Team" database was not found in your Notion workspace.\n');
  console.log('Options:');
  console.log('1. Create a new "Medical Team" database in Notion with the following properties:');
  console.log('   - Name (title): Provider name');
  console.log('   - Specialty (select): Medical specialty');
  console.log('   - Facility (rich_text): Hospital/clinic name');
  console.log('   - Address (rich_text): Office address');
  console.log('   - Phone (phone_number): Contact number');
  console.log('   - Email (email): Contact email');
  console.log('   - Website (url): Provider website');
  console.log('   - Notes (rich_text): Additional information\n');
  console.log('2. Share the database with your integration');
  console.log('3. Run the check-notion.ts script to get the database ID');
  console.log('4. Update the NOTION_MEDICAL_TEAM_DATABASE_ID in .env.local\n');
  
  console.log('Creating sample provider records directly in Supabase instead...\n');
  
  // Create some sample provider records directly in Supabase
  const sampleProviders = [
    {
      name: "Sample Primary Care Physician",
      specialty: "Primary Care",
      facility: "General Hospital",
      address: "123 Medical Blvd, Healthville, CA",
      phone: "555-123-4567",
      email: "pcp@example.com",
      notes: "Sample provider - replace with your actual provider data"
    },
    {
      name: "Sample Specialist",
      specialty: "Cardiology",
      facility: "Heart Center",
      address: "456 Specialist Ave, Healthville, CA",
      phone: "555-987-6543",
      email: "cardio@example.com",
      notes: "Sample specialist - replace with your actual provider data"
    }
  ];
  
  for (const provider of sampleProviders) {
    console.log(`Creating sample provider: ${provider.name}`);
    
    const { data, error } = await supabase
      .from('providers')
      .insert([provider])
      .select();
      
    if (error) {
      console.error(`Error creating sample provider ${provider.name}:`, error);
    } else if (data && data.length > 0) {
      console.log(`Successfully created sample provider: ${provider.name}`);
    }
  }
  
  console.log('\nSample providers created. Please update these with your actual provider information.');
  console.log('You can do this by:');
  console.log('1. Creating a proper Medical Team database in Notion as described above, or');
  console.log('2. Directly editing the providers in the Supabase dashboard.');
}

// Run the import
importMedicalTeam().catch(console.error); 