import path from 'path';
import fs from 'fs';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import readline from 'readline';
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

// Types for our extracted data
interface LabResult {
  test_name: string;
  category?: string;
  date?: string;
  result: string;
  unit?: string;
  reference_range?: string;
  is_abnormal?: boolean;
  notes?: string;
  source_file?: string;
}

interface Visit {
  title: string;
  date?: string;
  provider?: string;
  location?: string;
  diagnosis?: string[];
  notes?: string;
  visit_type?: string;
  source_file?: string;
}

// Function to safely parse a date and return ISO string
function parseDate(dateStr?: string): string {
  if (!dateStr) return new Date().toISOString();
  
  try {
    // First try to parse the ISO date directly
    const date = new Date(dateStr);
    
    // Check if the date is valid (not Invalid Date)
    if (!isNaN(date.getTime())) {
      return date.toISOString();
    }
    
    // If we reach here, parsing failed
    console.warn(`Could not parse date: ${dateStr}, using current date instead.`);
    return new Date().toISOString();
  } catch (error) {
    console.warn(`Error parsing date: ${dateStr}, using current date instead.`);
    return new Date().toISOString();
  }
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
  
  // Check if files exist (try both .json and .clean.json extensions)
  let labResultsFile = path.join(dataDir, 'lab-results.clean.json');
  if (!fs.existsSync(labResultsFile)) {
    labResultsFile = path.join(dataDir, 'lab-results.json');
  }
  
  let visitsFile = path.join(dataDir, 'visits.clean.json');
  if (!fs.existsSync(visitsFile)) {
    visitsFile = path.join(dataDir, 'visits.json');
  }
  
  if (!fs.existsSync(labResultsFile) || !fs.existsSync(visitsFile)) {
    console.error('Extracted data files not found. Please run extraction script first.');
    rl.close();
    return;
  }
  
  // Load extracted data
  console.log('Loading extracted data...');
  
  let labResults: LabResult[] = [];
  let visits: Visit[] = [];
  
  try {
    const labResultsData = fs.readFileSync(labResultsFile, 'utf-8');
    labResults = JSON.parse(labResultsData);
    console.log(`Found ${labResults.length} lab results in ${path.basename(labResultsFile)}`);
  } catch (error) {
    console.error(`Error loading lab results: ${error instanceof Error ? error.message : String(error)}`);
  }
  
  try {
    const visitsData = fs.readFileSync(visitsFile, 'utf-8');
    visits = JSON.parse(visitsData);
    console.log(`Found ${visits.length} visits in ${path.basename(visitsFile)}`);
  } catch (error) {
    console.error(`Error loading visits: ${error instanceof Error ? error.message : String(error)}`);
  }
  
  // Validate data
  const validLabResults = labResults.filter(result => 
    result.test_name && typeof result.test_name === 'string'
  );
  
  const validVisits = visits.filter(visit => 
    visit.title && typeof visit.title === 'string'
  );
  
  if (validLabResults.length < labResults.length) {
    console.warn(`Filtered out ${labResults.length - validLabResults.length} invalid lab results.`);
  }
  
  if (validVisits.length < visits.length) {
    console.warn(`Filtered out ${visits.length - validVisits.length} invalid visits.`);
  }
  
  console.log(`Ready to import ${validLabResults.length} lab results and ${validVisits.length} visits.`);
  
  // Ask for confirmation
  const confirm = await prompt('\nDo you want to import this data to your Supabase database? (y/n): ');
  
  if (confirm.toLowerCase() !== 'y') {
    console.log('Import canceled.');
    rl.close();
    return;
  }
  
  // Import lab results
  let labResultsImported = 0;
  let labResultsSkipped = 0;
  let labResultsErrors = 0;
  
  if (validLabResults.length > 0) {
    console.log('\nImporting lab results...');
    
    // Create a progress indicator
    const progressInterval = Math.max(1, Math.floor(validLabResults.length / 10));
    
    for (let i = 0; i < validLabResults.length; i++) {
      const result = validLabResults[i];
      
      try {
        // Check if this lab result already exists
        const { data: existingResults, error: searchError } = await supabase
          .from('lab_results')
          .select('id')
          .eq('test_name', result.test_name)
          .eq('date', parseDate(result.date))
          .eq('result', result.result || (result.notes ? 'See notes' : 'No result'))
          .limit(1);
        
        if (searchError) {
          console.error(`Error checking for existing lab result: ${searchError.message}`);
        }
        
        if (existingResults && existingResults.length > 0) {
          // Skip this result as it already exists
          labResultsSkipped++;
          continue;
        }
        
        // Insert new lab result
        const { error: insertError } = await supabase
          .from('lab_results')
          .insert({
            test_name: result.test_name,
            category: result.category || 'Laboratory',
            date: parseDate(result.date),
            result: result.result || (result.notes ? 'See notes' : 'No result'),
            unit: result.unit || '',
            reference_range: result.reference_range || '',
            is_abnormal: result.is_abnormal || false,
            notes: result.notes || '',
          });
        
        if (insertError) {
          console.error(`Error importing lab result ${result.test_name}: ${insertError.message}`);
          labResultsErrors++;
        } else {
          labResultsImported++;
          
          // Show progress
          if (i % progressInterval === 0 || i === validLabResults.length - 1) {
            process.stdout.write(`\rProgress: ${i + 1}/${validLabResults.length} lab results processed`);
          }
        }
      } catch (error) {
        console.error(`Error processing lab result: ${error instanceof Error ? error.message : String(error)}`);
        labResultsErrors++;
      }
    }
    
    console.log('\nLab results import completed.');
    console.log(`✓ Imported: ${labResultsImported}`);
    console.log(`✓ Skipped (already exists): ${labResultsSkipped}`);
    console.log(`✗ Errors: ${labResultsErrors}`);
  }
  
  // Import visits as medical events
  let visitsImported = 0;
  let visitsSkipped = 0;
  let visitsErrors = 0;
  
  if (validVisits.length > 0) {
    console.log('\nImporting visits as medical events...');
    
    // Create a progress indicator
    const progressInterval = Math.max(1, Math.floor(validVisits.length / 10));
    
    for (let i = 0; i < validVisits.length; i++) {
      const visit = validVisits[i];
      
      try {
        // Check if this visit already exists
        const { data: existingVisits, error: searchError } = await supabase
          .from('medical_events')
          .select('id')
          .eq('title', visit.title)
          .eq('date', parseDate(visit.date))
          .limit(1);
        
        if (searchError) {
          console.error(`Error checking for existing visit: ${searchError.message}`);
        }
        
        if (existingVisits && existingVisits.length > 0) {
          // Skip this visit as it already exists
          visitsSkipped++;
          continue;
        }
        
        // Create provider if needed
        let providerId = null;
        
        if (visit.provider && visit.provider.trim() !== '') {
          // Try to find existing provider
          const { data: providers, error: providerSearchError } = await supabase
            .from('providers')
            .select('id')
            .eq('name', visit.provider)
            .limit(1);
          
          if (providerSearchError) {
            console.error(`Error searching for provider: ${providerSearchError.message}`);
          }
          
          if (providers && providers.length > 0) {
            providerId = providers[0].id;
          } else {
            // Create new provider
            const { data: newProvider, error: providerInsertError } = await supabase
              .from('providers')
              .insert({
                name: visit.provider,
                specialty: visit.visit_type || 'Primary Care',
                facility: visit.location || '',
              })
              .select();
            
            if (providerInsertError) {
              console.error(`Error creating provider: ${providerInsertError.message}`);
            } else if (newProvider && newProvider.length > 0) {
              providerId = newProvider[0].id;
            }
          }
        }
        
        // Prepare diagnosis notes if available
        let notes = visit.notes || '';
        if (visit.diagnosis && visit.diagnosis.length > 0) {
          const diagnosisText = visit.diagnosis.filter(d => d && d.trim() !== '').join('\n- ');
          if (diagnosisText.trim() !== '') {
            notes = `Diagnosis:\n- ${diagnosisText}\n\n${notes}`;
          }
        }
        
        // Insert visit as medical event
        const { error: insertError } = await supabase
          .from('medical_events')
          .insert({
            title: visit.title,
            description: notes?.substring(0, 200) || '',
            event_type: 'appointment',
            date: parseDate(visit.date),
            location: visit.location || '',
            provider_id: providerId,
            notes: notes,
          });
        
        if (insertError) {
          console.error(`Error importing visit ${visit.title}: ${insertError.message}`);
          visitsErrors++;
        } else {
          visitsImported++;
          
          // Show progress
          if (i % progressInterval === 0 || i === validVisits.length - 1) {
            process.stdout.write(`\rProgress: ${i + 1}/${validVisits.length} visits processed`);
          }
        }
      } catch (error) {
        console.error(`Error processing visit: ${error instanceof Error ? error.message : String(error)}`);
        visitsErrors++;
      }
    }
    
    console.log('\nVisits import completed.');
    console.log(`✓ Imported: ${visitsImported}`);
    console.log(`✓ Skipped (already exists): ${visitsSkipped}`);
    console.log(`✗ Errors: ${visitsErrors}`);
  }
  
  console.log('\nImport process completed successfully.');
  rl.close();
}

// Run the script
importData().catch(error => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);
}); 