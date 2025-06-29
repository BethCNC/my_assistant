import dotenv from 'dotenv';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import type { Database } from '../lib/supabase/database.types';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials. Check your .env file.');
  process.exit(1);
}

const supabase = createClient<Database>(supabaseUrl, supabaseServiceKey);

async function showCounts() {
  console.log('\n===== Database Record Counts =====');
  
  // Count providers
  const { data: providers, error: providersError } = await supabase
    .from('providers')
    .select('id', { count: 'exact' });
    
  if (providersError) {
    console.error('Error counting providers:', providersError);
  } else {
    console.log(`Providers: ${providers.length}`);
  }
  
  // Count conditions
  const { data: conditions, error: conditionsError } = await supabase
    .from('conditions')
    .select('id', { count: 'exact' });
    
  if (conditionsError) {
    console.error('Error counting conditions:', conditionsError);
  } else {
    console.log(`Conditions: ${conditions.length}`);
  }
  
  // Count medical events
  const { data: events, error: eventsError } = await supabase
    .from('medical_events')
    .select('id', { count: 'exact' });
    
  if (eventsError) {
    console.error('Error counting medical events:', eventsError);
  } else {
    console.log(`Medical Events: ${events.length}`);
  }
  
  // Count lab results
  const { data: labs, error: labsError } = await supabase
    .from('lab_results')
    .select('id', { count: 'exact' });
    
  if (labsError) {
    console.error('Error counting lab results:', labsError);
  } else {
    console.log(`Lab Results: ${labs.length}`);
  }
  
  // Count symptoms
  const { data: symptoms, error: symptomsError } = await supabase
    .from('symptoms')
    .select('id', { count: 'exact' });
    
  if (symptomsError) {
    console.error('Error counting symptoms:', symptomsError);
  } else {
    console.log(`Symptoms: ${symptoms ? symptoms.length : 0}`);
  }
}

// Run the script
showCounts().catch(console.error); 