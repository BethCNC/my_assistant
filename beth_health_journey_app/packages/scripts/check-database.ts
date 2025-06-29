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

async function checkProviders() {
  console.log('\n===== Providers =====');
  const { data, error } = await supabase
    .from('providers')
    .select('*')
    .order('created_at', { ascending: false });
    
  if (error) {
    console.error('Error fetching providers:', error);
    return;
  }
  
  console.log(`Found ${data.length} providers:`);
  data.forEach(provider => {
    console.log(`- ${provider.name} (${provider.specialty || 'No specialty'})`);
  });
}

async function checkConditions() {
  console.log('\n===== Conditions =====');
  const { data, error } = await supabase
    .from('conditions')
    .select('*, providers(name)')
    .order('created_at', { ascending: false });
    
  if (error) {
    console.error('Error fetching conditions:', error);
    return;
  }
  
  console.log(`Found ${data.length} conditions:`);
  data.forEach(condition => {
    console.log(`- ${condition.name} (Status: ${condition.status}, Severity: ${condition.severity})`);
    if (condition.providers) {
      console.log(`  Provider: ${(condition.providers as any).name || 'Unknown'}`);
    }
  });
}

async function checkMedicalEvents() {
  console.log('\n===== Medical Events =====');
  const { data, error } = await supabase
    .from('medical_events')
    .select('*, providers(name)')
    .order('date', { ascending: false });
    
  if (error) {
    console.error('Error fetching medical events:', error);
    return;
  }
  
  console.log(`Found ${data.length} medical events:`);
  data.forEach(event => {
    console.log(`- ${event.title} (${event.event_type}, Date: ${new Date(event.date).toLocaleDateString()})`);
    if (event.providers) {
      console.log(`  Provider: ${(event.providers as any).name || 'Unknown'}`);
    }
  });
}

async function checkLabResults() {
  console.log('\n===== Lab Results =====');
  const { data, error } = await supabase
    .from('lab_results')
    .select('*, medical_events(title), providers(name)')
    .order('date', { ascending: false });
    
  if (error) {
    console.error('Error fetching lab results:', error);
    return;
  }
  
  console.log(`Found ${data.length} lab results:`);
  data.forEach(result => {
    console.log(`- ${result.test_name}: ${result.result} ${result.unit || ''}`);
    console.log(`  Reference Range: ${result.reference_range || 'Not provided'}`);
    console.log(`  Abnormal: ${result.is_abnormal ? 'Yes' : 'No'}`);
    if (result.medical_events) {
      console.log(`  Event: ${(result.medical_events as any).title || 'Unknown'}`);
    }
    if (result.providers) {
      console.log(`  Provider: ${(result.providers as any).name || 'Unknown'}`);
    }
  });
}

async function main() {
  console.log('Checking imported FHIR data in the database...');
  
  await checkProviders();
  await checkConditions();
  await checkMedicalEvents();
  await checkLabResults();
  
  console.log('\n===== Database Check Complete =====');
}

main().catch(console.error); 