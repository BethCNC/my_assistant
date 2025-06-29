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

async function createTables() {
  try {
    // Create symptoms table
    const { error: symptomsError } = await supabase
      .rpc('create_symptoms_table');
    
    if (symptomsError) {
      throw new Error(`Error creating symptoms table: ${symptomsError.message}`);
    }
    console.log('Successfully created symptoms table');

    // Create medical event symptoms table
    const { error: eventSymptomsError } = await supabase
      .rpc('create_medical_event_symptoms_table');
    
    if (eventSymptomsError) {
      throw new Error(`Error creating medical_event_symptoms table: ${eventSymptomsError.message}`);
    }
    console.log('Successfully created medical_event_symptoms table');

  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

createTables(); 