import path from 'path';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

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

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Check the symptoms and junction tables
async function checkSymptomsTables() {
  console.log('\n=== Checking Symptoms Tables ===\n');
  
  try {
    // Check the symptoms table
    console.log('Checking symptoms table...');
    const { data: symptoms, error: symptomsError } = await supabase
      .from('symptoms')
      .select('*')
      .limit(10);
    
    if (symptomsError) {
      console.error('Error accessing symptoms table:', symptomsError.message);
      console.error('This may indicate the table does not exist or there are permission issues.');
    } else {
      console.log(`Found ${symptoms?.length || 0} symptoms in the database.`);
      if (symptoms && symptoms.length > 0) {
        console.log('Sample symptom:', JSON.stringify(symptoms[0], null, 2));
      }
    }
    
    // Check the junction table
    console.log('\nChecking medical_event_symptoms table...');
    const { data: junctionRecords, error: junctionError } = await supabase
      .from('medical_event_symptoms')
      .select('*')
      .limit(10);
    
    if (junctionError) {
      console.error('Error accessing medical_event_symptoms table:', junctionError.message);
      console.error('This may indicate the table does not exist or there are permission issues.');
    } else {
      console.log(`Found ${junctionRecords?.length || 0} relationships in the database.`);
      if (junctionRecords && junctionRecords.length > 0) {
        console.log('Sample relationship:', JSON.stringify(junctionRecords[0], null, 2));
        
        // Get details for the first relationship
        if (junctionRecords[0].medical_event_id && junctionRecords[0].symptom_id) {
          console.log('\nFetching details for the first relationship...');
          
          // Get medical event details
          const { data: event } = await supabase
            .from('medical_events')
            .select('*')
            .eq('id', junctionRecords[0].medical_event_id)
            .single();
          
          // Get symptom details
          const { data: symptom } = await supabase
            .from('symptoms')
            .select('*')
            .eq('id', junctionRecords[0].symptom_id)
            .single();
          
          console.log('Related medical event:', event ? JSON.stringify(event, null, 2) : 'Not found');
          console.log('Related symptom:', symptom ? JSON.stringify(symptom, null, 2) : 'Not found');
        }
      }
    }
    
    // Check the schema of the tables
    console.log('\nChecking table schemas...');
    
    // For symptoms table
    const { data: symptomsSchema, error: symptomsSchemaError } = await supabase
      .rpc('get_table_definition', { table_name: 'symptoms' });
    
    if (symptomsSchemaError) {
      console.error('Error getting symptoms table schema:', symptomsSchemaError.message);
    } else {
      console.log('Symptoms table schema:', symptomsSchema);
    }
    
    // For junction table
    const { data: junctionSchema, error: junctionSchemaError } = await supabase
      .rpc('get_table_definition', { table_name: 'medical_event_symptoms' });
    
    if (junctionSchemaError) {
      console.error('Error getting medical_event_symptoms table schema:', junctionSchemaError.message);
    } else {
      console.log('Medical_event_symptoms table schema:', junctionSchema);
    }
    
  } catch (error) {
    if (error instanceof Error) {
      console.error('Unexpected error:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  }
}

// Run the checks
checkSymptomsTables().finally(() => {
  console.log('\nCheck completed.');
}); 