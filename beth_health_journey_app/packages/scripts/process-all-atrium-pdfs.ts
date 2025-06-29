import path from 'path';
import fs from 'fs';
import { execSync } from 'child_process';
import crypto from 'crypto';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import readline from 'readline';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Supabase client if credentials are available
let supabase: any = null;
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string;

if (supabaseUrl && supabaseServiceKey) {
  supabase = createClient(supabaseUrl, supabaseServiceKey);
}

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

// Set up directories
const pdfBaseDir = path.join(process.cwd(), 'data/atrium-exports');
const allImportDir = path.join(pdfBaseDir, 'all_import');
const labResultsDir = path.join(pdfBaseDir, 'lab-results');
const conditionsDir = path.join(pdfBaseDir, 'conditions');
const medicationsDir = path.join(pdfBaseDir, 'medications');
const appointmentsDir = path.join(pdfBaseDir, 'appointments');
const generalDir = path.join(pdfBaseDir, 'general');
const extractedDataDir = path.join(pdfBaseDir, 'extracted-data');

// Create directory if it doesn't exist
function ensureDirectoryExists(directoryPath: string) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
}

// Generate a hash for file content to help identify duplicates
function generateFileHash(filePath: string): string {
  try {
    const fileBuffer = fs.readFileSync(filePath);
    const hashSum = crypto.createHash('sha256');
    hashSum.update(fileBuffer);
    return hashSum.digest('hex');
  } catch (error) {
    console.error(`Error generating hash for ${filePath}:`, error);
    return '';
  }
}

// Get full text content of a PDF
function getPdfText(filePath: string): string {
  try {
    // Try using pdftotext (if installed)
    try {
      return execSync(`pdftotext "${filePath}" -`, { encoding: 'utf-8' });
    } catch (e) {
      // If pdftotext fails, try a different approach
      console.log(`Note: pdftotext not available. Install via 'brew install poppler' for better results.`);
      
      // On MacOS, try using textutil as a fallback
      try {
        const tempFile = path.join(process.cwd(), 'temp_pdf_text.txt');
        execSync(`textutil -convert txt -stdout "${filePath}" > "${tempFile}"`, { encoding: 'utf-8' });
        const content = fs.readFileSync(tempFile, 'utf-8');
        fs.unlinkSync(tempFile);
        return content;
      } catch (e2) {
        console.log(`Unable to extract PDF text content. Please install pdftotext.`);
        return '';
      }
    }
  } catch (error) {
    console.error(`Error extracting content from ${filePath}: ${error}`);
    return '';
  }
}

// Function to classify a PDF based on its content and filename
function classifyPdf(filePath: string): { category: string; destination: string } {
  const fileName = path.basename(filePath);
  const content = getPdfText(filePath).toLowerCase();
  
  // Debug what content we're getting
  console.log(`\nAnalyzing file: ${fileName}`);
  
  // Default classification
  let destination = generalDir;
  let category = 'general';
  
  // Check for test/lab results
  if (
    content.includes('test results') || 
    content.includes('lab results') || 
    content.includes('laboratory results') ||
    content.includes('test details') ||
    content.includes('reference range') ||
    content.includes('result trends') ||
    fileName.toLowerCase().includes('test') ||
    fileName.toLowerCase().includes('lab') ||
    fileName.toLowerCase().includes('cmp') ||
    fileName.toLowerCase().includes('tsh') ||
    fileName.toLowerCase().includes('t4') ||
    fileName.toLowerCase().includes('comprehensive')
  ) {
    console.log(`  ✓ Classified as: Lab Result`);
    destination = labResultsDir;
    category = 'labResults';
  }
  // Check for conditions/diagnoses
  else if (
    content.includes('diagnosis') || 
    content.includes('condition') || 
    content.includes('assessment') ||
    content.includes('problem list')
  ) {
    console.log(`  ✓ Classified as: Medical Condition`);
    destination = conditionsDir;
    category = 'conditions';
  }
  // Check for medications/prescriptions
  else if (
    content.includes('medication') || 
    content.includes('prescription') || 
    content.includes('dosage') ||
    content.includes('pharmacy')
  ) {
    console.log(`  ✓ Classified as: Medication`);
    destination = medicationsDir;
    category = 'medications';
  }
  // Check for appointments/visits
  else if (
    content.includes('appointment') || 
    content.includes('visit details') || 
    content.includes('visit summary') ||
    content.includes('office visit') ||
    content.includes('past visit') ||
    content.includes('after visit') ||
    content.includes('dr.') ||
    fileName.toLowerCase().includes('visit') ||
    fileName.toLowerCase().includes('gp_') ||
    fileName.toLowerCase().includes('dr')
  ) {
    console.log(`  ✓ Classified as: Appointment/Visit`);
    destination = appointmentsDir;
    category = 'appointments';
  }
  else {
    console.log(`  ✓ Classified as: General/Uncategorized`);
  }
  
  return { category, destination };
}

// Check if a file is a duplicate of any file in the specified directory
function isDuplicate(filePath: string, targetDir: string): boolean {
  if (!fs.existsSync(targetDir)) {
    return false;
  }

  const fileHash = generateFileHash(filePath);
  if (!fileHash) return false;
  
  const existingFiles = fs.readdirSync(targetDir)
    .filter(file => file.toLowerCase().endsWith('.pdf'))
    .map(file => path.join(targetDir, file));
  
  for (const existingFile of existingFiles) {
    const existingHash = generateFileHash(existingFile);
    if (fileHash === existingHash) {
      console.log(`  ⚠️ Duplicate found: ${path.basename(filePath)} matches ${path.basename(existingFile)}`);
      return true;
    }
  }
  
  return false;
}

// Recursively get all PDF files from a directory
function getAllPdfFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) {
    return [];
  }
  
  let results: string[] = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      // Recursively add PDFs from subdirectories
      results = [...results, ...getAllPdfFiles(fullPath)];
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.pdf')) {
      results.push(fullPath);
    }
  }
  
  return results;
}

// Extract date from filename or path
function extractDateFromPath(filePath: string): string | null {
  // Try to extract year from the path (e.g., all_import/2025/file.pdf)
  const yearMatch = filePath.match(/\/20(\d{2})\//);
  if (yearMatch) {
    return `20${yearMatch[1]}`;
  }
  
  // Try to extract from filename if it contains a date
  const fileName = path.basename(filePath);
  const dateMatch = fileName.match(/(\d{1,2})[-_](\d{1,2})[-_](\d{2,4})/);
  if (dateMatch) {
    return dateMatch[3].length === 2 ? `20${dateMatch[3]}` : dateMatch[3];
  }
  
  return null;
}

/**
 * Main function to process all PDF files from the all_import directory
 */
async function processAllAtriumPDFs() {
  console.log('===== Atrium Health PDF Processing =====');
  console.log('This script will process all PDFs from the all_import directory, categorize them, and check for duplicates.\n');
  
  // Create all necessary directories
  ensureDirectoryExists(labResultsDir);
  ensureDirectoryExists(conditionsDir);
  ensureDirectoryExists(medicationsDir);
  ensureDirectoryExists(appointmentsDir);
  ensureDirectoryExists(generalDir);
  ensureDirectoryExists(extractedDataDir);
  
  // Get all PDFs from the all_import directory recursively
  console.log('Scanning all_import directory for PDFs...');
  const allImportPdfs = getAllPdfFiles(allImportDir);
  
  if (allImportPdfs.length === 0) {
    console.log('No PDF files found in the all_import directory.');
    rl.close();
    return;
  }
  
  console.log(`Found ${allImportPdfs.length} PDF files to process.`);
  
  // Confirm processing
  const confirmProcess = await prompt('\nDo you want to categorize and process these files? (y/n): ');
  
  if (confirmProcess.toLowerCase() !== 'y') {
    console.log('Processing canceled.');
    rl.close();
    return;
  }
  
  // Count results
  const results = {
    labResults: 0,
    conditions: 0,
    medications: 0,
    appointments: 0,
    general: 0,
    duplicates: 0,
  };
  
  // Process each PDF
  for (const filePath of allImportPdfs) {
    const { category, destination } = classifyPdf(filePath);
    const fileName = path.basename(filePath);
    
    // Skip if it's a duplicate
    if (isDuplicate(filePath, destination)) {
      console.log(`  Skipping duplicate file: ${fileName}`);
      results.duplicates++;
      continue;
    }
    
    const year = extractDateFromPath(filePath);
    let destPath = path.join(destination, fileName);
    
    // If we have a year, create a subdirectory for the year
    if (year) {
      const yearDir = path.join(destination, year);
      ensureDirectoryExists(yearDir);
      destPath = path.join(yearDir, fileName);
      console.log(`  File from ${year}, saving to year-specific folder`);
    }
    
    // Delete file if it exists in destination (to avoid issues with copying)
    if (fs.existsSync(destPath)) {
      console.log(`  File already exists at destination. Generating unique name.`);
      // Generate a unique name
      const fileExt = path.extname(fileName);
      const fileBase = path.basename(fileName, fileExt);
      destPath = path.join(path.dirname(destPath), `${fileBase}_${Date.now()}${fileExt}`);
    }
    
    // Copy to the appropriate folder
    try {
      fs.copyFileSync(filePath, destPath);
      console.log(`  ✓ Copied to: ${destPath}`);
      results[category as keyof typeof results]++;
    } catch (error) {
      console.error(`  ✕ Error copying file: ${error}`);
    }
  }
  
  // Report results
  console.log('\n===== PROCESSING SUMMARY =====');
  console.log(`Lab Results: ${results.labResults} files`);
  console.log(`Conditions: ${results.conditions} files`);
  console.log(`Medications: ${results.medications} files`);
  console.log(`Appointments: ${results.appointments} files`);
  console.log(`General/Uncategorized: ${results.general} files`);
  console.log(`Duplicates Skipped: ${results.duplicates} files`);
  console.log(`\nFiles organized in: ${pdfBaseDir}`);
  
  // Ask if user wants to extract data
  const extractData = await prompt('\nDo you want to extract data from the newly categorized files? (y/n): ');
  
  if (extractData.toLowerCase() === 'y') {
    console.log('\nRunning data extraction script...');
    
    try {
      // Run the extraction script using execSync
      const output = execSync('npx ts-node scripts/extract-atrium-pdf-data.ts', { 
        encoding: 'utf-8',
        stdio: 'inherit' // This will show the script's output in real-time
      });
    } catch (error) {
      console.error('Error running extraction script:', error);
    }
  }
  
  console.log('\nNext Steps:');
  console.log('1. Review the categorized PDFs in each folder');
  console.log('2. Run extract-atrium-pdf-data.ts to extract data if not already done');
  console.log('3. Run import-health-data.ts to import the extracted data to your database');
  
  rl.close();
}

// Run the script
processAllAtriumPDFs().catch((error) => {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);
}); 