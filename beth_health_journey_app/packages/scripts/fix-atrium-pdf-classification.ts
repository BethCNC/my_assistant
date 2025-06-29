import path from 'path';
import fs from 'fs';
import { execSync } from 'child_process';

/**
 * Helper script to properly categorize Atrium Health PDFs based on content
 * This script is specifically designed to fix incorrect categorization
 */

// Set up directories
const pdfBaseDir = path.join(process.cwd(), 'data/atrium-exports');
const labResultsDir = path.join(pdfBaseDir, 'lab-results');
const conditionsDir = path.join(pdfBaseDir, 'conditions');
const medicationsDir = path.join(pdfBaseDir, 'medications');
const appointmentsDir = path.join(pdfBaseDir, 'appointments');
const generalDir = path.join(pdfBaseDir, 'general');

// Create directory if it doesn't exist
function ensureDirectoryExists(directoryPath: string) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
}

// Get first 100 lines of a PDF as text using pdftotext if available
function getPdfContentPreview(filePath: string): string {
  try {
    // Try using pdftotext (if installed)
    try {
      return execSync(`pdftotext "${filePath}" - | head -n 100`, { encoding: 'utf-8' });
    } catch (e) {
      // If pdftotext fails, try a different approach
      console.log(`Note: pdftotext not available. Install via 'brew install poppler' for better results.`);
      
      // On MacOS, try using textutil as a fallback
      try {
        const tempFile = path.join(process.cwd(), 'temp_pdf_text.txt');
        execSync(`textutil -convert txt -stdout "${filePath}" > "${tempFile}"`, { encoding: 'utf-8' });
        const content = fs.readFileSync(tempFile, 'utf-8').slice(0, 10000);
        fs.unlinkSync(tempFile);
        return content;
      } catch (e2) {
        console.log(`Unable to extract PDF text content. Using filename only for classification.`);
        return path.basename(filePath);
      }
    }
  } catch (error) {
    console.error(`Error extracting content from ${filePath}: ${error}`);
    return path.basename(filePath);
  }
}

// Function to classify a PDF based on its content and filename
function classifyPdf(filePath: string): { category: string; destination: string } {
  const fileName = path.basename(filePath);
  const content = getPdfContentPreview(filePath).toLowerCase();
  
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
    fileName.toLowerCase().includes('test')
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
    fileName.toLowerCase().includes('visit')
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

/**
 * Main function to fix categorization of Atrium Health PDF exports
 */
function fixAtriumPDFClassification() {
  console.log('===== Atrium Health PDF Categorization Fix =====');
  console.log('This script will analyze and properly categorize Atrium Health PDFs.\n');
  
  // Create all necessary directories
  ensureDirectoryExists(pdfBaseDir);
  ensureDirectoryExists(labResultsDir);
  ensureDirectoryExists(conditionsDir);
  ensureDirectoryExists(medicationsDir);
  ensureDirectoryExists(appointmentsDir);
  ensureDirectoryExists(generalDir);
  
  // Get all PDFs directly in the base directory
  let baseFiles: string[] = [];
  try {
    baseFiles = fs.readdirSync(pdfBaseDir)
      .filter(file => file.toLowerCase().endsWith('.pdf'))
      .map(file => path.join(pdfBaseDir, file));
  } catch (error) {
    console.error('Error reading base directory:', error);
    process.exit(1);
  }
  
  // Check subdirectories for PDFs as well (in case files were already moved)
  const subDirs = [labResultsDir, conditionsDir, medicationsDir, appointmentsDir, generalDir];
  let subDirFiles: string[] = [];
  
  subDirs.forEach(dir => {
    if (fs.existsSync(dir)) {
      try {
        const files = fs.readdirSync(dir)
          .filter(file => file.toLowerCase().endsWith('.pdf'))
          .map(file => path.join(dir, file));
        subDirFiles = [...subDirFiles, ...files];
      } catch (error) {
        console.error(`Error reading directory ${dir}:`, error);
      }
    }
  });
  
  // Combine all PDF files
  const allPdfFiles = [...baseFiles, ...subDirFiles];
  
  if (allPdfFiles.length === 0) {
    console.log('No PDF files found to categorize.');
    process.exit(0);
  }
  
  console.log(`Found ${allPdfFiles.length} PDF files to analyze.`);
  
  // Reset counts
  const results = {
    labResults: 0,
    conditions: 0,
    medications: 0,
    appointments: 0,
    general: 0
  };
  
  // Process each PDF
  allPdfFiles.forEach(filePath => {
    const { category, destination } = classifyPdf(filePath);
    const fileName = path.basename(filePath);
    const destPath = path.join(destination, fileName);
    
    // Skip if the file is already in the correct location
    if (filePath === destPath) {
      console.log(`  File is already in the correct directory.`);
      results[category as keyof typeof results]++;
      return;
    }
    
    // Delete file if it exists in destination (to avoid issues with copying)
    if (fs.existsSync(destPath)) {
      fs.unlinkSync(destPath);
    }
    
    // Copy to the appropriate folder
    fs.copyFileSync(filePath, destPath);
    
    // Remove original file if it's not the same as destination
    if (filePath !== destPath) {
      fs.unlinkSync(filePath);
    }
    
    results[category as keyof typeof results]++;
  });
  
  // Report results
  console.log('\n===== ORGANIZATION SUMMARY =====');
  console.log(`Lab Results: ${results.labResults} files`);
  console.log(`Conditions: ${results.conditions} files`);
  console.log(`Medications: ${results.medications} files`);
  console.log(`Appointments: ${results.appointments} files`);
  console.log(`General/Uncategorized: ${results.general} files`);
  console.log(`\nFiles organized in: ${pdfBaseDir}`);
  
  console.log('\nNext Steps:');
  console.log('1. Review the categorized PDFs in each folder');
  console.log('2. Use data extraction scripts to import this data to your database');
}

// Run the script
fixAtriumPDFClassification(); 