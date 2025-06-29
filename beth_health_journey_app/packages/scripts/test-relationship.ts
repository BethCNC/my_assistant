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

async function testRelationship() {
  try {
    console.log('Starting simple relationship test...');

    // Check if medical_event_symptoms table exists
    console.log('Checking if table exists...');
    const { data: tableCheck, error: tableCheckError } = await supabase
      .from('medical_event_symptoms')
      .select('id')
      .limit(1);

    if (tableCheckError) {
      console.error('Error checking table:', tableCheckError.message);
      return;
    }

    console.log('Table exists, fetching a sample event and symptom...');

    // Fetch one medical event
    const { data: event, error: eventError } = await supabase
      .from('medical_events')
      .select('id, title')
      .limit(1);

    if (eventError || !event || event.length === 0) {
      console.error('Error fetching event:', eventError?.message || 'No events found');
      return;
    }

    // Fetch one symptom
    const { data: symptom, error: symptomError } = await supabase
      .from('symptoms')
      .select('id, name')
      .limit(1);

    if (symptomError || !symptom || symptom.length === 0) {
      console.error('Error fetching symptom:', symptomError?.message || 'No symptoms found');
      return;
    }

    console.log(`Found event: ${event[0].title} (${event[0].id})`);
    console.log(`Found symptom: ${symptom[0].name} (${symptom[0].id})`);

    // Try inserting a record
    console.log('Attempting to insert a relationship record...');
    
    const { data: insertData, error: insertError } = await supabase
      .from('medical_event_symptoms')
      .insert([{
        medical_event_id: event[0].id,
        symptom_id: symptom[0].id,
        severity: 5,
        notes: 'Test relationship'
      }]);

    if (insertError) {
      console.error('Error inserting relationship:', insertError.message);
      
      if (insertError.message.includes('violates row-level security')) {
        console.log('\nThis is a RLS (Row-Level Security) issue!');
        console.log('The user associated with the service key may not have permission.');
        console.log('\nLet\'s try with admin privileges by disabling RLS...');
        
        // Use .rpc to call a function that bypasses RLS (if available)
        const { data: bypassData, error: bypassError } = await supabase.rpc('admin_insert_medical_event_symptom', {
          event_id: event[0].id,
          symp_id: symptom[0].id,
          sev: 5,
          note: 'Test relationship with admin privileges'
        });
        
        if (bypassError) {
          console.error('Error with admin insert attempt:', bypassError.message);
          console.log('\nAlternative approach:');
          console.log('1. Go to Supabase Dashboard');
          console.log('2. Go to Authentication > Policies');
          console.log('3. Find the medical_event_symptoms table');
          console.log('4. Temporarily disable RLS or create a more permissive policy');
          console.log('5. Run this script again');
        } else {
          console.log('Admin insert succeeded!');
        }
      }
      return;
    }

    console.log('Successfully inserted relationship record!');

    // Verify the insertion
    const { data: verifyData, error: verifyError } = await supabase
      .from('medical_event_symptoms')
      .select('*, medical_events(title), symptoms(name)')
      .eq('medical_event_id', event[0].id)
      .eq('symptom_id', symptom[0].id)
      .limit(1);

    if (verifyError) {
      console.error('Error verifying insertion:', verifyError.message);
      return;
    }

    if (!verifyData || verifyData.length === 0) {
      console.log('Verification failed: Record not found after insertion');
      return;
    }

    console.log('Verification successful! Found the relationship:');
    console.log(verifyData[0]);

  } catch (error) {
    if (error instanceof Error) {
      console.error('Unknown error:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  }
}

// Run the function
testRelationship().catch(console.error).finally(() => {
  console.log('Test completed.');
}); 