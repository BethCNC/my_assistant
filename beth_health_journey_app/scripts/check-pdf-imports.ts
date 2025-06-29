import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import { Database } from '../lib/supabase/database.types';

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

async function checkImports() {
  console.log('===== Checking PDF Import Results =====\n');
  
  // Get yesterday's date as ISO string
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayISO = yesterday.toISOString();
  
  // Check recent lab results (imported from PDFs)
  console.log('--- Lab Results ---');
  try {
    const { data: labResults, error } = await supabase
      .from('lab_results')
      .select('*')
      .gt('created_at', yesterdayISO)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching lab results:', error.message);
    } else if (!labResults || labResults.length === 0) {
      console.log('No recently imported lab results found.');
    } else {
      console.log(`Found ${labResults.length} recently imported lab results.`);
      console.log('\nSample lab results:');
      
      // Display 5 most recent lab results
      for (let i = 0; i < Math.min(5, labResults.length); i++) {
        const result = labResults[i];
        console.log(`\n[${i + 1}] ${result.test_name}`);
        console.log(`    Date: ${new Date(result.date).toLocaleDateString()}`);
        console.log(`    Result: ${result.result}`);
        console.log(`    Category: ${result.category || 'N/A'}`);
        if (result.reference_range) {
          console.log(`    Reference Range: ${result.reference_range}`);
        }
        if (result.notes) {
          console.log(`    Notes: ${result.notes.substring(0, 100)}${result.notes.length > 100 ? '...' : ''}`);
        }
      }
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
  }
  
  // Check recent medical events (visits imported from PDFs)
  console.log('\n--- Recent Medical Events ---');
  try {
    const { data: events, error } = await supabase
      .from('medical_events')
      .select('*')
      .gt('created_at', yesterdayISO)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching medical events:', error.message);
    } else if (!events || events.length === 0) {
      console.log('No recently imported medical events found.');
    } else {
      console.log(`Found ${events.length} recently imported medical events.`);
      console.log('\nSample medical events:');
      
      // Display 5 most recent events
      for (let i = 0; i < Math.min(5, events.length); i++) {
        const event = events[i];
        console.log(`\n[${i + 1}] ${event.title}`);
        console.log(`    Date: ${new Date(event.date).toLocaleDateString()}`);
        console.log(`    Type: ${event.event_type || 'N/A'}`);
        console.log(`    Location: ${event.location || 'N/A'}`);
        if (event.notes) {
          console.log(`    Notes: ${event.notes.substring(0, 100)}${event.notes.length > 100 ? '...' : ''}`);
        }
      }
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
  }
}

// Run the script
checkImports().catch(error => {
  console.error('Error:', error?.message || 'Unknown error');
  process.exit(1);
}); 