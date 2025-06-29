import path from 'path';
import fs from 'fs';
import readline from 'readline';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
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
 * Opens a URL in the default browser
 */
async function openUrl(url: string): Promise<void> {
  try {
    // Dynamic import of 'open' package
    const openModule = await import('open');
    const open = openModule.default;
    await open(url);
    return;
  } catch (error) {
    console.error('Failed to open URL in browser. Please navigate to it manually:', url);
    console.error('Error:', error);
  }
}

/**
 * Main function to guide user through manual data extraction
 */
async function manualAtriumDataExtraction() {
  console.log('===== Atrium Health Manual Data Extraction Helper =====');
  console.log('This script will guide you through manually extracting your health data\n');
  
  // Create directory for exported files
  const exportDir = path.join(process.cwd(), 'data/atrium-exports');
  ensureDirectoryExists(exportDir);
  
  // Step 1: Direct user to log in to MyChart
  console.log('Step 1: Log in to your Atrium Health MyChart account');
  const openBrowser = await prompt('Would you like to open the Atrium Health MyChart website now? (y/n): ');
  
  if (openBrowser.toLowerCase() === 'y') {
    await openUrl('https://my.atriumhealth.org/MyChart/Authentication/Login');
    console.log('Browser opened to Atrium Health login page');
  }
  
  // Step 2: Guide for downloading conditions
  console.log('\nStep 2: Download your medical conditions data');
  console.log('Instructions:');
  console.log('1. In your MyChart account, navigate to "Health > Medical Conditions"');
  console.log('2. Look for any download or export option (often in CSV format)');
  console.log('3. If no direct export is available, you may need to manually copy the data or take screenshots');
  
  const conditionsDownloaded = await prompt('Were you able to download or export your medical conditions? (y/n): ');
  
  if (conditionsDownloaded.toLowerCase() === 'y') {
    const conditionsFilePath = await prompt('Please provide the full path to the downloaded conditions file: ');
    if (fs.existsSync(conditionsFilePath)) {
      // Copy file to our data directory
      const fileName = path.basename(conditionsFilePath);
      const destPath = path.join(exportDir, 'conditions-' + fileName);
      fs.copyFileSync(conditionsFilePath, destPath);
      console.log(`File copied to ${destPath}`);
    } else {
      console.log(`File not found at ${conditionsFilePath}. Please check the path and try again.`);
    }
  } else {
    console.log('That\'s okay. Let\'s continue with other data types.');
  }
  
  // Step 3: Guide for downloading lab results
  console.log('\nStep 3: Download your lab results data');
  console.log('Instructions:');
  console.log('1. In your MyChart account, navigate to "Health > Test Results"');
  console.log('2. Look for any download or export option (often in CSV format)');
  console.log('3. If no direct export is available, many results have a "Download/Print" button for each test');
  
  const labsDownloaded = await prompt('Were you able to download or export your lab results? (y/n): ');
  
  if (labsDownloaded.toLowerCase() === 'y') {
    const labsFilePath = await prompt('Please provide the full path to the downloaded lab results file: ');
    if (fs.existsSync(labsFilePath)) {
      // Copy file to our data directory
      const fileName = path.basename(labsFilePath);
      const destPath = path.join(exportDir, 'labs-' + fileName);
      fs.copyFileSync(labsFilePath, destPath);
      console.log(`File copied to ${destPath}`);
    } else {
      console.log(`File not found at ${labsFilePath}. Please check the path and try again.`);
    }
  } else {
    console.log('That\'s okay. Let\'s continue with other data types.');
  }
  
  // Step 4: Guide for downloading appointments
  console.log('\nStep 4: Download your appointments data');
  console.log('Instructions:');
  console.log('1. In your MyChart account, navigate to "Visits > Appointments and Visits"');
  console.log('2. Look for any download or export option (often in CSV format)');
  console.log('3. If no direct export is available, you may need to manually copy the data or take screenshots');
  
  const appointmentsDownloaded = await prompt('Were you able to download or export your appointments? (y/n): ');
  
  if (appointmentsDownloaded.toLowerCase() === 'y') {
    const appointmentsFilePath = await prompt('Please provide the full path to the downloaded appointments file: ');
    if (fs.existsSync(appointmentsFilePath)) {
      // Copy file to our data directory
      const fileName = path.basename(appointmentsFilePath);
      const destPath = path.join(exportDir, 'appointments-' + fileName);
      fs.copyFileSync(appointmentsFilePath, destPath);
      console.log(`File copied to ${destPath}`);
    } else {
      console.log(`File not found at ${appointmentsFilePath}. Please check the path and try again.`);
    }
  } else {
    console.log('That\'s okay. Let\'s continue with other data types.');
  }
  
  // Step 5: Guide for downloading medications
  console.log('\nStep 5: Download your medications data');
  console.log('Instructions:');
  console.log('1. In your MyChart account, navigate to "Health > Medications"');
  console.log('2. Look for any download or export option (often in CSV format)');
  console.log('3. If no direct export is available, you may need to manually copy the data or take screenshots');
  
  const medsDownloaded = await prompt('Were you able to download or export your medications? (y/n): ');
  
  if (medsDownloaded.toLowerCase() === 'y') {
    const medsFilePath = await prompt('Please provide the full path to the downloaded medications file: ');
    if (fs.existsSync(medsFilePath)) {
      // Copy file to our data directory
      const fileName = path.basename(medsFilePath);
      const destPath = path.join(exportDir, 'medications-' + fileName);
      fs.copyFileSync(medsFilePath, destPath);
      console.log(`File copied to ${destPath}`);
    } else {
      console.log(`File not found at ${medsFilePath}. Please check the path and try again.`);
    }
  } else {
    console.log('That\'s okay. We\'ll try another approach.');
  }
  
  // Step 6: Advise on requesting medical records
  console.log('\nStep 6: Request comprehensive medical records');
  console.log('Instructions:');
  console.log('1. In MyChart, look for "Medical Records Request" or similar option');
  console.log('2. You can typically request a full copy of your medical records in electronic format');
  console.log('3. This will often include more comprehensive data than available through the web interface');
  
  await prompt('Press Enter when you\'ve noted these instructions...');
  
  // Step 7: Guide for downloading CCD/CDA file
  console.log('\nStep 7: Download consolidated clinical document (CCD/CDA)');
  console.log('Instructions:');
  console.log('1. In MyChart, look for "Download My Record" or "Share My Record" option');
  console.log('2. This often provides a CCD/CDA file in XML format that contains structured health data');
  console.log('3. This file can be imported into many health apps and contains comprehensive data');
  
  const ccdDownloaded = await prompt('Were you able to download a CCD/CDA file? (y/n): ');
  
  if (ccdDownloaded.toLowerCase() === 'y') {
    const ccdFilePath = await prompt('Please provide the full path to the downloaded CCD/CDA file: ');
    if (fs.existsSync(ccdFilePath)) {
      // Copy file to our data directory
      const fileName = path.basename(ccdFilePath);
      const destPath = path.join(exportDir, 'ccd-' + fileName);
      fs.copyFileSync(ccdFilePath, destPath);
      console.log(`File copied to ${destPath}`);
      
      // Here we could add logic to parse the CCD/CDA XML and import it
      console.log('\nNote: In a future update, we can add functionality to parse and import CCD/CDA data into your database.');
    } else {
      console.log(`File not found at ${ccdFilePath}. Please check the path and try again.`);
    }
  } else {
    console.log('That\'s okay. There are other options available.');
  }
  
  // Summary
  console.log('\n===== DATA EXTRACTION SUMMARY =====');
  
  // List collected files
  console.log('Files collected in', exportDir, ':');
  if (fs.existsSync(exportDir)) {
    const files = fs.readdirSync(exportDir);
    if (files.length === 0) {
      console.log('No files were collected.');
    } else {
      files.forEach(file => console.log(`- ${file}`));
    }
  }
  
  console.log('\nNext steps:');
  console.log('1. We can create a parser for any exported files to import them into your database');
  console.log('2. You can request a complete medical record download from Atrium Health');
  console.log('3. Consider using a health data aggregator app (like Apple Health) that can connect to Atrium');
  
  rl.close();
}

// Run the script
manualAtriumDataExtraction().catch((error: any) => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);
}); 