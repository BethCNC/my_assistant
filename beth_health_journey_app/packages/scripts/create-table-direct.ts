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

const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

async function createTables() {
  try {
    console.log('Checking if tables need to be created...');

    // Check if medical_event_symptoms table exists
    const { data: medicalEventSymptomsTest, error: testError } = await supabase
      .from('medical_event_symptoms')
      .select('id')
      .limit(1);

    if (testError && testError.message.includes('relation "public.medical_event_symptoms" does not exist')) {
      console.log('medical_event_symptoms table does not exist. We need to create it.');
      
      // Instructions for manual creation
      console.log('\n==================================');
      console.log('IMPORTANT: You need to execute the following SQL in your Supabase SQL Editor:');
      console.log('1. Go to your Supabase dashboard');
      console.log('2. Click on "SQL Editor"');
      console.log('3. Create a new query and paste the contents of scripts/create_medical_event_symptoms.sql');
      console.log('4. Execute the query');
      console.log('==================================\n');

      console.log('Would you like to try creating a simple version of the table now?');
      console.log('This might work but may not include all RLS policies.\n');
      
      // Try using a simpler approach with built-in PostgreSQL statements
      await createSimpleTable();
    } else {
      console.log('medical_event_symptoms table already exists');
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error checking/creating tables:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  }
}

async function createSimpleTable() {
  try {
    // Create a simple linking table just to enable basic functionality
    console.log('Attempting to create a simple version of medical_event_symptoms...');
    
    // This is not ideal, but we use an edge function or RPC to create this properly
    // For now, we create a minimal table
    console.log('This approach will not work directly with Supabase client.');
    console.log('You need to use the SQL Editor in the Supabase dashboard instead.');
    
    // If we had an edge function available, we would call it like this:
    // const { data, error } = await supabase.functions.invoke('create-tables', {});
    // if (error) throw error;
    // console.log('Table created via edge function!', data);
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error creating simple table:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  }
}

// Run the function
createTables().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
}); 