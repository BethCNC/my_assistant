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

// Notion database ID for medical calendar
const MEDICAL_CALENDAR_DATABASE_ID = process.env.NOTION_MEDICAL_CALENDAR_DATABASE_ID;

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
        return property.relation?.map((item: any) => item.id) || [];
      default:
        return null;
    }
  } catch (error) {
    console.error(`Error extracting property value:`, error);
    return null;
  }
}

// Function to safely convert arrays to JSON
function safeJsonArray(arr: any): any {
  if (!arr) return null;
  
  try {
    if (Array.isArray(arr)) {
      return arr;
    }
    return [arr];
  } catch (error) {
    return null;
  }
}

async function importMedicalCalendar() {
  if (!MEDICAL_CALENDAR_DATABASE_ID) {
    console.error('Missing NOTION_MEDICAL_CALENDAR_DATABASE_ID environment variable');
    process.exit(1);
  }

  try {
    // Fetch medical events from Notion
    console.log('Fetching medical events from Notion...');
    console.log(`Using database ID: ${MEDICAL_CALENDAR_DATABASE_ID}`);
    
    const response = await notion.databases.query({
      database_id: MEDICAL_CALENDAR_DATABASE_ID as string,
    });

    const events = response.results;
    console.log(`Found ${events.length} medical events in Notion.`);

    // First, get all conditions and providers from Supabase to map relations
    const { data: conditions, error: conditionsError } = await supabase
      .from('conditions')
      .select('id, name');
      
    if (conditionsError) {
      console.error('Error fetching conditions:', conditionsError);
      process.exit(1);
    }
    
    const { data: providers, error: providersError } = await supabase
      .from('providers')
      .select('id, name');
      
    if (providersError) {
      console.error('Error fetching providers:', providersError);
      process.exit(1);
    }
    
    const conditionMap = new Map();
    conditions?.forEach(condition => {
      conditionMap.set(condition.name.toLowerCase(), condition.id);
    });
    
    const providerMap = new Map();
    providers?.forEach(provider => {
      providerMap.set(provider.name.toLowerCase(), provider.id);
    });
    
    console.log(`Loaded ${conditionMap.size} conditions and ${providerMap.size} providers for mapping`);

    // Process each event and insert into Supabase
    for (const event of events) {
      console.log(`Processing event with ID: ${event.id}`);
      
      // Safely access properties
      if (!('properties' in event)) {
        console.error(`Event ${event.id} doesn't have properties field`);
        continue;
      }
      
      const properties = event.properties;
      
      // Get related entities
      const relatedConditionName = getPropertyValue(properties['Related Condition']);
      const relatedProviderName = getPropertyValue(properties['Provider']);
      
      // Map to Supabase IDs
      let conditionId = null;
      let providerId = null;
      
      if (relatedConditionName) {
        conditionId = conditionMap.get(relatedConditionName.toLowerCase());
        if (!conditionId) {
          console.log(`  Could not find condition: ${relatedConditionName}`);
        }
      }
      
      if (relatedProviderName) {
        providerId = providerMap.get(relatedProviderName.toLowerCase());
        if (!providerId) {
          console.log(`  Could not find provider: ${relatedProviderName}`);
        }
      }
      
      // Get date with fallback to today
      let eventDate = getPropertyValue(properties.Date);
      if (!eventDate) {
        eventDate = new Date().toISOString();
      }
      
      // Extract and map event type to valid Supabase types
      let eventType = getPropertyValue(properties.Type)?.toLowerCase() || 'appointment';
      // Map to valid event types in Supabase: appointment, procedure, test, hospitalization, lab_result
      // Make sure to map various Notion values to these specific types
      if (eventType.includes('lab') || eventType.includes('result') || eventType === 'lab result') {
        eventType = 'lab_result';
      } else if (eventType.includes('doctor') || eventType.includes('note') || eventType.includes('appt')) {
        eventType = 'appointment';
      } else if (eventType.includes('image') || eventType.includes('scan')) {
        eventType = 'test';
      } else if (eventType.includes('hospital') || eventType.includes('admission')) {
        eventType = 'hospitalization';
      } else if (eventType.includes('surgery') || eventType.includes('procedure')) {
        eventType = 'procedure';
      } else {
        // Default to appointment for unrecognized types
        eventType = 'appointment';
      }
      
      // Extract medical event information
      const eventData = {
        title: getPropertyValue(properties.Name) || 'Unnamed Event',
        description: getPropertyValue(properties.Description),
        event_type: eventType,
        date: eventDate,
        location: getPropertyValue(properties.Location),
        provider_id: providerId,
        condition_id: conditionId,
        notes: getPropertyValue(properties.Notes),
        documents: safeJsonArray(getPropertyValue(properties.Documents)),
      };

      console.log(`Importing medical event: ${eventData.title}`);
      
      // Insert into Supabase
      const { data: insertedEvent, error } = await supabase
        .from('medical_events')
        .insert([eventData])
        .select();

      if (error) {
        console.error(`Error importing medical event ${eventData.title}:`, error);
      } else if (insertedEvent && insertedEvent.length > 0) {
        console.log(`Successfully imported medical event: ${eventData.title}`);
      }
    }

    console.log('Import complete!');

  } catch (error) {
    console.error('❌ Error importing medical calendar:', error);
    console.error('Error details:', error instanceof Error ? error.message : JSON.stringify(error));
    process.exit(1);
  }
}

// Run the import
importMedicalCalendar().catch(console.error); 