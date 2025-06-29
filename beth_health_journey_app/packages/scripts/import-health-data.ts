import path from 'path';
import fs from 'fs';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import readline from 'readline';

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

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to prompt for user input
function prompt(question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

// Main function to import data
async function importData() {
  console.log('===== Health Data Import Tool =====');
  console.log('This script will import extracted health data into your Supabase database.\n');
  
  const dataDir = path.join(process.cwd(), 'data/atrium-exports/extracted-data');
  
  // Check if extracted data directory exists
  if (!fs.existsSync(dataDir)) {
    console.error('Extracted data directory not found. Please run extraction script first.');
    rl.close();
    return;
  }
  
  // Check if files exist
  const labResultsFile = path.join(dataDir, 'lab-results.json');
  const visitsFile = path.join(dataDir, 'visits.json');
  
  if (!fs.existsSync(labResultsFile) || !fs.existsSync(visitsFile)) {
    console.error('Extracted data files not found. Please run extraction script first.');
    rl.close();
    return;
  }
  
  // Load extracted data
  console.log('Loading extracted data...');
  const labResults = JSON.parse(fs.readFileSync(labResultsFile, 'utf-8'));
  const visits = JSON.parse(fs.readFileSync(visitsFile, 'utf-8'));
  
  console.log(`Found ${labResults.length} lab results and ${visits.length} visits to import.`);
  
  // Ask for confirmation
  const confirm = await prompt('\nDo you want to import this data to your Supabase database? (y/n): ');
  
  if (confirm.toLowerCase() !== 'y') {
    console.log('Import canceled.');
    rl.close();
    return;
  }
  
  // Import lab results
  if (labResults.length > 0) {
    console.log('\nImporting lab results...');
    
    for (const result of labResults) {
      try {
        // Simple insert
        const { error } = await supabase
          .from('lab_results')
          .insert({
            test_name: result.test_name,
            category: result.category || 'General',
            date: result.date ? new Date(result.date).toISOString() : new Date().toISOString(),
            result: result.result,
            unit: result.unit || '',
            reference_range: result.reference_range || '',
            is_abnormal: result.is_abnormal || false,
            notes: result.notes || '',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        
        if (error) {
          console.error(`Error importing lab result ${result.test_name}: ${error.message}`);
        } else {
          console.log(`✓ Imported lab result: ${result.test_name}`);
        }
      } catch (error) {
        console.error(`Error processing lab result: ${error}`);
      }
    }
  }
  
  // Import visits as medical events
  if (visits.length > 0) {
    console.log('\nImporting visits as medical events...');
    
    for (const visit of visits) {
      try {
        // Create provider if needed
        let providerId = null;
        
        if (visit.provider) {
          // Try to find or create provider
          const { data: providers } = await supabase
            .from('providers')
            .select('id')
            .eq('name', visit.provider)
            .limit(1);
          
          if (providers && providers.length > 0) {
            providerId = providers[0].id;
          } else {
            // Create new provider
            const { data: newProvider, error } = await supabase
              .from('providers')
              .insert({
                name: visit.provider,
                specialty: 'Primary Care',
                facility: visit.location || '',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
              })
              .select();
            
            if (!error && newProvider) {
              providerId = newProvider[0].id;
            }
          }
        }
        
        // Insert visit as medical event
        const { error } = await supabase
          .from('medical_events')
          .insert({
            title: visit.title,
            description: visit.notes?.substring(0, 200) || '',
            event_type: 'appointment',
            date: visit.date ? new Date(visit.date).toISOString() : new Date().toISOString(),
            location: visit.location || '',
            provider_id: providerId,
            notes: visit.notes || '',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        
        if (error) {
          console.error(`Error importing visit ${visit.title}: ${error.message}`);
        } else {
          console.log(`✓ Imported visit: ${visit.title}`);
        }
      } catch (error) {
        console.error(`Error processing visit: ${error}`);
      }
    }
  }
  
  console.log('\nImport process completed.');
  rl.close();
}

// Run the script
importData().catch(error => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);});