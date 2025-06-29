import * as dotenv from 'dotenv';

// Load environment variables from .env files
dotenv.config({ path: '.env.local' });
dotenv.config({ path: '.env' });

console.log('Environment variables loaded:');
console.log(`NEXT_PUBLIC_SUPABASE_URL: ${process.env.NEXT_PUBLIC_SUPABASE_URL ? '✅ Set' : '❌ Not set'}`);
console.log(`NEXT_PUBLIC_SUPABASE_ANON_KEY: ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? '✅ Set' : '❌ Not set'}`);

// Import the Supabase client AFTER loading environment variables
import { supabase } from '../lib/supabase/client';

async function checkAppDatabaseConnection() {
  console.log('Checking Supabase connection via app client...');
  
  try {
    // Try to fetch some conditions
    const { data: conditions, error: conditionsError } = await supabase
      .from('conditions')
      .select('id, name, description')
      .limit(3);
      
    if (conditionsError) {
      console.error('❌ Error fetching conditions:', conditionsError);
    } else {
      console.log('✅ Successfully fetched conditions:');
      console.table(conditions);
    }
    
    // Try to fetch some symptoms
    const { data: symptoms, error: symptomsError } = await supabase
      .from('symptoms')
      .select('id, name, description, severity')
      .limit(3);
      
    if (symptomsError) {
      console.error('❌ Error fetching symptoms:', symptomsError);
    } else {
      console.log('✅ Successfully fetched symptoms:');
      console.table(symptoms);
    }
    
    // Try to fetch providers
    const { data: providers, error: providersError } = await supabase
      .from('providers')
      .select('id, name, specialty, facility')
      .limit(3);
      
    if (providersError) {
      console.error('❌ Error fetching providers:', providersError);
    } else {
      console.log('✅ Successfully fetched providers:');
      console.table(providers);
    }
    
    console.log('✅ Database connection test completed!');
  } catch (error) {
    console.error('❌ Error checking database connection:', error);
  }
}

// Run the check
checkAppDatabaseConnection(); 