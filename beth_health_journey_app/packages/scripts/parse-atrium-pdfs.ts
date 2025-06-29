import path from 'path';
import fs from 'fs';
import readline from 'readline';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import { exec } from 'child_process';
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

// Create directory if it doesn't exist
function ensureDirectoryExists(directoryPath: string) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
}

/**
 * Main function to organize and parse Atrium Health PDF exports
 */
async function organizeAtriumPDFs() {
  console.log('===== Atrium Health PDF Organizer =====');
  console.log('This script helps organize and process PDFs exported from Atrium Health MyChart.\n');
  
  // Step 1: Set up directories
  const pdfBaseDir = path.join(process.cwd(), 'data/atrium-exports');
  const labResultsDir = path.join(pdfBaseDir, 'lab-results');
  const conditionsDir = path.join(pdfBaseDir, 'conditions');
  const medicationsDir = path.join(pdfBaseDir, 'medications');
  const appointmentsDir = path.join(pdfBaseDir, 'appointments');
  const generalDir = path.join(pdfBaseDir, 'general');
  
  ensureDirectoryExists(pdfBaseDir);
  ensureDirectoryExists(labResultsDir);
  ensureDirectoryExists(conditionsDir);
  ensureDirectoryExists(medicationsDir);
  ensureDirectoryExists(appointmentsDir);
  ensureDirectoryExists(generalDir);
  
  // Step 2: Ask for the download folder
  console.log('Step 1: Locate your downloaded PDFs');
  const downloadFolder = await prompt('Enter the path to the folder containing your downloaded PDFs: ');
  
  if (!fs.existsSync(downloadFolder)) {
    console.error(`Folder not found: ${downloadFolder}`);
    process.exit(1);
  }
  
  // Step 3: List PDFs in the download folder
  console.log('\nScanning for PDFs...');
  
  let pdfFiles: string[] = [];
  try {
    const files = fs.readdirSync(downloadFolder);
    pdfFiles = files.filter(file => file.toLowerCase().endsWith('.pdf'));
    
    if (pdfFiles.length === 0) {
      console.log('No PDF files found in the specified folder.');
      process.exit(0);
    }
    
    console.log(`Found ${pdfFiles.length} PDF files.`);
  } catch (error) {
    console.error('Error reading directory:', error);
    process.exit(1);
  }
  
  // Step 4: Organize PDFs by type
  console.log('\nOrganizing PDFs by type...');
  
  const results = {
    labResults: 0,
    conditions: 0,
    medications: 0,
    appointments: 0,
    general: 0
  };
  
  for (const file of pdfFiles) {
    const filePath = path.join(downloadFolder, file);
    const fileName = path.basename(file);
    
    // Try to categorize the PDF based on filename
    let destination = generalDir;
    let category = 'general';
    
    if (fileName.toLowerCase().includes('lab') || 
        fileName.toLowerCase().includes('test') || 
        fileName.toLowerCase().includes('result')) {
      destination = labResultsDir;
      category = 'labResults';
    } else if (fileName.toLowerCase().includes('condition') || 
               fileName.toLowerCase().includes('diagnosis')) {
      destination = conditionsDir;
      category = 'conditions';
    } else if (fileName.toLowerCase().includes('medication') || 
               fileName.toLowerCase().includes('med list') ||
               fileName.toLowerCase().includes('prescription')) {
      destination = medicationsDir;
      category = 'medications';
    } else if (fileName.toLowerCase().includes('appointment') || 
               fileName.toLowerCase().includes('visit')) {
      destination = appointmentsDir;
      category = 'appointments';
    }
    
    // Make a copy to the appropriate folder
    const destPath = path.join(destination, fileName);
    fs.copyFileSync(filePath, destPath);
    results[category as keyof typeof results]++;
  }
  
  // Step 5: Report results
  console.log('\n===== ORGANIZATION SUMMARY =====');
  console.log(`Lab Results: ${results.labResults} files`);
  console.log(`Conditions: ${results.conditions} files`);
  console.log(`Medications: ${results.medications} files`);
  console.log(`Appointments: ${results.appointments} files`);
  console.log(`General/Uncategorized: ${results.general} files`);
  console.log(`\nFiles organized in: ${pdfBaseDir}`);
  
  // Step 6: Offer to install PDF parsing tools
  console.log('\nFor extracting data from PDFs, you can install additional tools:');
  const installTools = await prompt('Would you like to install pdf-parse and pdfjs-dist for future PDF extraction? (y/n): ');
  
  if (installTools.toLowerCase() === 'y') {
    console.log('\nInstalling PDF parsing packages...');
    return new Promise<void>((resolve, reject) => {
      exec('npm install pdf-parse pdfjs-dist', (error, stdout, stderr) => {
        if (error) {
          console.error(`Error installing packages: ${error.message}`);
          reject(error);
          return;
        }
        if (stderr) {
          console.log(`stderr: ${stderr}`);
        }
        console.log(stdout);
        console.log('PDF parsing packages installed successfully.');
        console.log('\nIn a future update, we can add functionality to extract structured data from these PDFs.');
        resolve();
      });
    });
  }
  
  console.log('\nNext Steps:');
  console.log('1. Review the organized PDFs in the designated folders');
  console.log('2. In a future update, we can implement:');
  console.log('   - PDF text extraction to pull data from these documents');
  console.log('   - Parsing lab results for test names, values, and reference ranges');
  console.log('   - Importing structured data into your database');
  
  rl.close();
}

// Run the script
organizeAtriumPDFs().catch((error: any) => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);
}); 