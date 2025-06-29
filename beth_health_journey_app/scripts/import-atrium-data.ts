import path from 'path';
import fs from 'fs';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import readline from 'readline';
import type { Database } from '../lib/supabase/database.types';

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

// Format date for database
function formatDate(date: Date | null | string): string | null {
  if (!date) return null;
  
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toISOString();
}

// Generate a UUID v4
function uuidv4(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Import lab results to Supabase
 */
async function importLabResults(labResultsData: any[]) {
  console.log('Importing lab results...');
  
  for (const labResult of labResultsData) {
    try {
      // Check if provider exists or create new
      let providerId = null;
      if (labResult.provider) {
        // Try to find provider
        const { data: existingProviders } = await supabase
          .from('providers')
          .select('id, name')
          .ilike('name', `%${labResult.provider.split(',')[0]}%`);
        
        if (existingProviders && existingProviders.length > 0) {
          providerId = existingProviders[0].id;
        } else {
          // Create provider
          const { data: newProvider, error } = await supabase
            .from('providers')
            .insert({
              name: labResult.provider,
              specialty: '',
              facility: '',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            })
            .select();
          
          if (error) {
            console.error(`Error creating provider: ${error.message}`);
          } else if (newProvider) {
            providerId = newProvider[0].id;
          }
        }
      }
      
      // Format lab result for database
      const labResultRecord = {
        test_name: labResult.test_name,
        category: labResult.category || '',
        date: formatDate(labResult.date) || new Date().toISOString(),
        result: labResult.result,
        unit: labResult.unit || '',
        reference_range: labResult.reference_range || '',
        is_abnormal: labResult.is_abnormal || false,
        provider_id: providerId,
        notes: labResult.notes || '',
        file_url: '', // No file URL in this case
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      // Insert lab result
      const { error } = await supabase
        .from('lab_results')
        .insert(labResultRecord);
      
      if (error) {
        console.error(`Error importing lab result '${labResult.test_name}': ${error.message}`);
      } else {
        console.log(`✓ Imported lab result: ${labResult.test_name}`);
      }
    } catch (error) {
      console.error(`Error processing lab result: ${error}`);
    }
  }
}

/**
 * Import medical events (visits) to Supabase
 */
async function importMedicalEvents(visitsData: any[]) {
  console.log('Importing visit data as medical events...');
  
  for (const visit of visitsData) {
    try {
      // Check if provider exists or create new
      let providerId = null;
      if (visit.provider) {
        // Try to find provider
        const { data: existingProviders } = await supabase
          .from('providers')
          .select('id, name')
          .ilike('name', `%${visit.provider.split(',')[0]}%`);
        
        if (existingProviders && existingProviders.length > 0) {
          providerId = existingProviders[0].id;
        } else {
          // Create provider
          const { data: newProvider, error } = await supabase
            .from('providers')
            .insert({
              name: visit.provider,
              specialty: 'Primary Care',
              facility: visit.location || '',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            })
            .select();
          
          if (error) {
            console.error(`Error creating provider: ${error.message}`);
          } else if (newProvider) {
            providerId = newProvider[0].id;
          }
        }
      }
      
      // Format medical event for database
      const medicalEvent = {
        title: visit.title || 'Office Visit',
        description: visit.notes || '',
        event_type: 'appointment',
        date: formatDate(visit.date) || new Date().toISOString(),
        location: visit.location || '',
        provider_id: providerId,
        condition_id: null, // No specific condition linked
        treatment_id: null, // No specific treatment linked
        notes: visit.notes || '',
        documents: [], // No documents linked
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      // Insert medical event
      const { error } = await supabase
        .from('medical_events')
        .insert(medicalEvent);
      
      if (error) {
        console.error(`Error importing visit '${visit.title}': ${error.message}`);
      } else {
        console.log(`✓ Imported visit: ${visit.title}`);
      }
      
      // Process diagnoses if any
      if (visit.diagnosis && visit.diagnosis.length > 0) {
        await importDiagnoses(visit.diagnosis, providerId);
      }
    } catch (error) {
      console.error(`Error processing visit: ${error}`);
    }
  }
}

/**
 * Import diagnoses as conditions to Supabase
 */
async function importDiagnoses(diagnoses: string[], providerId: string | null) {
  console.log('Importing diagnoses as conditions...');
  
  // Filter out non-diagnoses (like dates, orders, etc.)
  const validDiagnoses = diagnoses.filter(d => 
    !d.match(/^\d+\/\d+\/\d+$/) && // Not a date
    !d.includes('Order:') &&      // Not an order
    !d.includes('Status:') &&     // Not a status
    !d.includes('Impression') &&  // Not an impression header
    !d.includes('DATE OF SERVICE') && // Not a service date header
    !d.includes('EXAM:') &&       // Not an exam header
    d.length >= 3                // Not too short
  );
  
  for (const diagnosisText of validDiagnoses) {
    try {
      // Check if this condition already exists
      const { data: existingConditions } = await supabase
        .from('conditions')
        .select('id, name')
        .ilike('name', `%${diagnosisText.substring(0, 30)}%`);
      
      if (existingConditions && existingConditions.length > 0) {
        console.log(`✓ Condition already exists: ${diagnosisText.substring(0, 50)}...`);
        continue;
      }
      
      // Format condition for database
      const condition = {
        name: diagnosisText,
        description: '',
        date_diagnosed: new Date().toISOString(),
        status: 'active',
        severity: 5, // Default middle severity
        category: determineConditionCategory(diagnosisText),
        notes: '',
        provider_id: providerId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      // Insert condition
      const { error } = await supabase
        .from('conditions')
        .insert(condition);
      
      if (error) {
        console.error(`Error importing condition '${diagnosisText}': ${error.message}`);
      } else {
        console.log(`✓ Imported condition: ${diagnosisText.substring(0, 50)}...`);
      }
    } catch (error) {
      console.error(`Error processing diagnosis: ${error}`);
    }
  }
}

/**
 * Determine the category of a condition based on its name
 */
function determineConditionCategory(conditionName: string): string {
  const name = conditionName.toLowerCase();
  
  if (name.includes('thyroid') || name.includes('hashimoto')) {
    return 'Endocrine';
  } else if (name.includes('diabetes') || name.includes('glucose') || name.includes('igt')) {
    return 'Metabolic';
  } else if (name.includes('hypertension') || name.includes('blood pressure') || name.includes('cholesterol') || name.includes('lipid')) {
    return 'Cardiovascular';
  } else if (name.includes('depression') || name.includes('anxiety') || name.includes('bipolar') || name.includes('ptsd')) {
    return 'Mental Health';
  } else if (name.includes('arthritis') || name.includes('joint') || name.includes('pain')) {
    return 'Musculoskeletal';
  } else if (name.includes('asthma') || name.includes('copd') || name.includes('lung')) {
    return 'Respiratory';
  } else if (name.includes('eds') || name.includes('ehlers') || name.includes('pots')) {
    return 'Connective Tissue';
  }
  
  return 'Other';
}

/**
 * Main function to import extracted Atrium Health data to Supabase
 */
async function importAtriumData() {
  console.log('===== Atrium Health Data Import =====');
  console.log('This script will import the extracted Atrium Health data into your Supabase database.\n');
  
  const pdfBaseDir = path.join(process.cwd(), 'data/atrium-exports');
  const outputDir = path.join(pdfBaseDir, 'extracted-data');
  
  const labResultsFile = path.join(outputDir, 'lab-results.json');
  const visitsFile = path.join(outputDir, 'visits.json');
  
  // Check if extracted data files exist
  if (!fs.existsSync(labResultsFile) || !fs.existsSync(visitsFile)) {
    console.error('Extracted data files not found. Please run extract-atrium-pdf-data.ts first.');
    process.exit(1);
  }
  
  // Load extracted data
  const labResults = JSON.parse(fs.readFileSync(labResultsFile, 'utf-8'));
  const visits = JSON.parse(fs.readFileSync(visitsFile, 'utf-8'));
  
  console.log(`Found ${labResults.length} lab results and ${visits.length} visits to import.`);
  
  // Confirm import
  const confirmImport = await prompt('\nDo you want to import this data to your Supabase database? (y/n): ');
  
  if (confirmImport.toLowerCase() !== 'y') {
    console.log('Import canceled.');
    rl.close();
    return;
  }
  
  // Import data
  await importLabResults(labResults);
  await importMedicalEvents(visits);
  
  console.log('\nData import completed!');
  rl.close();
}

// Run the script
importAtriumData().catch((error) => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1); // Run the script
importAtriumData().catch((error) => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);
});
