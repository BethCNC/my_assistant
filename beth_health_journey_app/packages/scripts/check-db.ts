import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';

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

async function checkTables() {
  try {
    // Check medical_events table
    console.log('Checking medical_events table...');
    const { data: medicalEvents, error: medicalEventsError } = await supabase
      .from('medical_events')
      .select('*')
      .limit(5);
    
    if (medicalEventsError) {
      console.error('Error fetching medical events:', medicalEventsError.message);
    } else {
      console.log(`Found ${medicalEvents.length} medical events.`);
      if (medicalEvents.length > 0) {
        console.log('Sample medical event:', JSON.stringify(medicalEvents[0], null, 2));
      }
    }

    // Check lab_results table
    console.log('\nChecking lab_results table...');
    const { data: labResults, error: labResultsError } = await supabase
      .from('lab_results')
      .select('*')
      .limit(5);
    
    if (labResultsError) {
      console.error('Error fetching lab results:', labResultsError.message);
    } else {
      console.log(`Found ${labResults.length} lab results.`);
      if (labResults.length > 0) {
        console.log('Sample lab result:', JSON.stringify(labResults[0], null, 2));
      }
    }

    // Check symptoms table
    const { data: symptoms, error: symptomsError } = await supabase
      .from('symptoms')
      .select('*');

    if (symptomsError) {
      console.log('\n=== Symptoms ===');
      console.log(`Error: ${symptomsError.message}`);
      console.log('Table might not exist yet.');
    } else {
      console.log('\n=== Symptoms ===');
      console.log(`Total records: ${symptoms?.length || 0}`);
      if (symptoms && symptoms.length > 0) {
        console.log('Sample records (first 3):');
        symptoms.slice(0, 3).forEach((symptom, index) => {
          console.log(`\n[${index + 1}] ${symptom.name}`);
          console.log(`    Severity: ${symptom.severity || 'N/A'}`);
          console.log(`    Description: ${symptom.description || 'N/A'}`);
        });
      }
    }

    // Check medical_event_symptoms table
    const { data: eventSymptoms, error: eventSymptomsError } = await supabase
      .from('medical_event_symptoms')
      .select('*');

    if (eventSymptomsError) {
      console.log('\n=== Medical Event Symptoms ===');
      console.log(`Error: ${eventSymptomsError.message}`);
      console.log('Table might not exist yet.');
    } else {
      console.log('\n=== Medical Event Symptoms ===');
      console.log(`Total records: ${eventSymptoms?.length || 0}`);
      if (eventSymptoms && eventSymptoms.length > 0) {
        console.log('Sample records (first 3):');
        eventSymptoms.slice(0, 3).forEach((relation, index) => {
          console.log(`\n[${index + 1}] Event ID: ${relation.medical_event_id}`);
          console.log(`    Symptom ID: ${relation.symptom_id}`);
          console.log(`    Severity: ${relation.severity || 'N/A'}`);
        });
      }
    }

    // Check providers table
    const { data: providers, error: providersError } = await supabase
      .from('providers')
      .select('*');

    if (providersError) {
      console.log('\n=== Providers ===');
      console.log(`Error: ${providersError.message}`);
      console.log('Table might not exist yet.');
    } else {
      console.log('\n=== Providers ===');
      console.log(`Total records: ${providers?.length || 0}`);
      if (providers && providers.length > 0) {
        console.log('Sample records (first 3):');
        providers.slice(0, 3).forEach((provider, index) => {
          console.log(`\n[${index + 1}] ${provider.name}`);
          console.log(`    Specialty: ${provider.specialty || 'N/A'}`);
          console.log(`    Facility: ${provider.facility || 'N/A'}`);
        });
      }
    }

    // Check conditions table
    const { data: conditions, error: conditionsError } = await supabase
      .from('conditions')
      .select('*');

    if (conditionsError) {
      console.log('\n=== Conditions ===');
      console.log(`Error: ${conditionsError.message}`);
      console.log('Table might not exist yet.');
    } else {
      console.log('\n=== Conditions ===');
      console.log(`Total records: ${conditions?.length || 0}`);
      if (conditions && conditions.length > 0) {
        console.log('Sample records (first 3):');
        conditions.slice(0, 3).forEach((condition, index) => {
          console.log(`\n[${index + 1}] ${condition.name}`);
          console.log(`    Status: ${condition.status || 'N/A'}`);
          console.log(`    Diagnosed: ${condition.date_diagnosed || 'N/A'}`);
        });
      }
    }

  } catch (error) {
    console.error('Error checking tables:', error);
  }
}

checkTables().catch(console.error); 