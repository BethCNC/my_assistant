import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function checkSymptoms() {
  try {
    // Check symptoms table
    const { data: symptoms, error: symptomsError } = await supabase
      .from('symptoms')
      .select('*');

    if (symptomsError) throw symptomsError;

    console.log('\n=== Symptoms in Database ===');
    console.log(`Total symptoms: ${symptoms?.length || 0}`);
    
    if (symptoms && symptoms.length > 0) {
      console.log('\nFirst 5 symptoms:');
      symptoms.slice(0, 5).forEach(symptom => {
        console.log(`- ${symptom.name} (Severity: ${symptom.severity || 'N/A'})`);
      });
    } else {
      console.log('No symptoms found in the database.');
    }

    // Check medical_event_symptoms table
    const { data: eventSymptoms, error: eventSymptomsError } = await supabase
      .from('medical_event_symptoms')
      .select('*');

    if (eventSymptomsError) throw eventSymptomsError;

    console.log('\n=== Symptom-Event Relationships ===');
    console.log(`Total relationships: ${eventSymptoms?.length || 0}`);

  } catch (error) {
    if (error instanceof Error) {
      console.error('Error:', error.message);
    } else {
      console.error('An unknown error occurred:', error);
    }
    process.exit(1);
  }
}

checkSymptoms().catch((error: unknown) => {
  if (error instanceof Error) {
    console.error('Error:', error.message);
  } else {
    console.error('Unknown error:', error);
  }
  process.exit(1);
}); 