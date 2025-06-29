import path from 'path';
import fs from 'fs';
import { execSync } from 'child_process';
import * as glob from 'glob';

// Set up directories
const pdfBaseDir = path.join(process.cwd(), 'data/atrium-exports');
const labResultsDir = path.join(pdfBaseDir, 'lab-results');
const appointmentsDir = path.join(pdfBaseDir, 'appointments');
const extractedDataDir = path.join(pdfBaseDir, 'extracted-data');

// Create directory if it doesn't exist
function ensureDirectoryExists(directoryPath: string) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
}

// Get full text content of a PDF
function getPdfText(filePath: string): string {
  try {
    // Try using pdftotext (if installed)
    try {
      return execSync(`pdftotext "${filePath}" -`, { encoding: 'utf-8' });
    } catch (e) {
      console.log(`Note: pdftotext not available for ${path.basename(filePath)}. Try installing via 'brew install poppler'.`);
      return '';
    }
  } catch (error) {
    console.error(`Error extracting content from ${filePath}: ${error}`);
    return '';
  }
}

// Process lab results PDFs
function processLabResults(maxFiles = 50): any[] {
  const results: any[] = [];
  
  // Get all PDF files in the lab-results directory and its subdirectories
  const labResultFiles = glob.sync('**/*.pdf', { 
    cwd: labResultsDir, 
    absolute: true,
    nocase: true
  });

  console.log(`Found ${labResultFiles.length} lab result PDFs. Processing up to ${maxFiles}.`);
  
  // Take a subset to prevent processing too many files
  const filesToProcess = labResultFiles.slice(0, maxFiles);
  
  for (const filePath of filesToProcess) {
    console.log(`\nExtracting data from: ${path.basename(filePath)}`);
    
    const content = getPdfText(filePath);
    if (!content) {
      console.log(`  No content extracted.`);
      continue;
    }
    
    // Extract date from content
    const dateMatch = content.match(/(?:Date of Service|DATE OF SERVICE|Test Date|Collection Date):\s*(\d{1,2}\/\d{1,2}\/\d{2,4})/i);
    const testDate = dateMatch ? new Date(dateMatch[1]) : null;
    
    // Extract test name - look for different patterns
    let testName = '';
    
    // Try to find test name from various patterns in the content
    const testNamePatterns = [
      /Test Name:\s*([^\n]+)/i,
      /EXAM:\s*([^\n]+)/i,
      /Test:\s*([^\n]+)/i,
      /(?:^|\n)([A-Z][A-Z, ]{4,}(?:\s*[\d\-]+)?)\s*(?:RESULT|Value|Reference|Range|UNITS|ORDERED)/m
    ];
    
    for (const pattern of testNamePatterns) {
      const match = content.match(pattern);
      if (match && match[1] && match[1].trim().length > 0) {
        testName = match[1].trim();
        break;
      }
    }
    
    // If still no test name, try the filename
    if (!testName) {
      const filename = path.basename(filePath, path.extname(filePath));
      if (filename.length > 3) {
        testName = filename.replace(/_/g, ' ');
      }
    }
    
    // If still no test name, skip this file
    if (!testName) {
      console.log(`  No test name found, skipping file.`);
      continue;
    }
    
    // Extract result, reference range, and abnormal flags
    const resultMatch = content.match(/(?:Result|Value):\s*([^\n]+)/i);
    const rangeMatch = content.match(/(?:Reference Range|Normal Range|Range):\s*([^\n]+)/i);
    const unitMatch = content.match(/(?:Units|UNITS):\s*([^\n]+)/i);
    
    // Check for abnormal flag
    const isAbnormal = content.includes('ABNORMAL') || 
                     content.includes('abnormal') || 
                     content.includes('Critical') || 
                     content.includes('Out of range') ||
                     content.includes('High') ||
                     content.includes('Low');
    
    // Determine category
    let category = 'General';
    if (content.includes('IMAGING') || content.includes('Radiology') || content.includes('X-ray') || 
        content.includes('MRI') || content.includes('CT scan') || content.includes('Ultrasound') ||
        testName.includes('XR') || testName.includes('US ') || testName.includes('MRI') || 
        testName.includes('CT ')) {
      category = 'Imaging';
    } else if (content.includes('Blood') || content.includes('CBC') || content.includes('Complete Blood Count')) {
      category = 'Blood Work';
    } else if (content.includes('Thyroid') || testName.includes('TSH') || testName.includes('T3') || testName.includes('T4')) {
      category = 'Thyroid';
    } else if (content.includes('Lipid') || content.includes('Cholesterol') || content.includes('Triglycerides')) {
      category = 'Lipids';
    } else if (content.includes('Liver') || content.includes('ALT') || content.includes('AST') || 
               content.includes('Bilirubin') || content.includes('Albumin')) {
      category = 'Liver Function';
    }
    
    // Extract notes - get a good chunk of useful text
    const notesMatch = content.match(/(?:IMPRESSION|Impression|FINDINGS|Findings|CONCLUSION|Conclusion|COMMENTS|Comments):\s*([^\n]+(?:\n(?!\n)[^\n]+)*)/i);
    const notes = notesMatch ? notesMatch[1].trim() : '';
    
    // Try to extract date from filename or content
    let date = testDate;
    if (!date) {
      // Try to extract from filename
      const fileNameDateMatch = path.basename(filePath).match(/(\d{1,2})[-_](\d{1,2})[-_](\d{2,4})/);
      if (fileNameDateMatch) {
        const year = fileNameDateMatch[3].length === 2 ? '20' + fileNameDateMatch[3] : fileNameDateMatch[3];
        const month = fileNameDateMatch[1].padStart(2, '0');
        const day = fileNameDateMatch[2].padStart(2, '0');
        date = new Date(`${year}-${month}-${day}`);
      }
      
      // If still no date, try from parent directory name (if it's a year)
      if (!date) {
        const parentDir = path.basename(path.dirname(filePath));
        if (/^(19|20)\d{2}$/.test(parentDir)) {
          date = new Date(`${parentDir}-01-01`);
        } else {
          // If still no date, use current date
          date = new Date();
        }
      }
    }
    
    // Create result object
    const result = {
      test_name: testName,
      result: resultMatch ? resultMatch[1].trim() : '',
      unit: unitMatch ? unitMatch[1].trim() : '',
      reference_range: rangeMatch ? rangeMatch[1].trim() : '',
      is_abnormal: isAbnormal,
      date: date.toISOString(),
      category,
      notes,
      source_file: path.basename(filePath)
    };
    
    results.push(result);
    console.log(`  Found lab result: ${result.test_name}`);
  }
  
  return results;
}

// Process visit/appointment PDFs
function processVisits(maxFiles = 10): any[] {
  const visits: any[] = [];
  
  // Get all PDF files in the appointments directory and its subdirectories
  const visitFiles = glob.sync('**/*.pdf', { 
    cwd: appointmentsDir, 
    absolute: true,
    nocase: true
  });
  
  console.log(`Found ${visitFiles.length} visit/appointment PDFs. Processing up to ${maxFiles}.`);
  
  // Take a subset to prevent processing too many files
  const filesToProcess = visitFiles.slice(0, maxFiles);
  
  for (const filePath of filesToProcess) {
    console.log(`\nExtracting data from: ${path.basename(filePath)}`);
    
    const content = getPdfText(filePath);
    if (!content) {
      console.log(`  No content extracted from file.`);
      continue;
    }
    
    // Extract visit title and date
    const titleMatch = content.match(/(?:Office Visit|Visit Details|After Visit Summary)(?:\s*[-:])?\s*([^\n]+)/i);
    const dateMatch = content.match(/(?:Date of Visit|Visit Date|DATE|Date):\s*(\d{1,2}\/\d{1,2}\/\d{2,4})/i);
    
    let visitTitle = '';
    let visitDate: Date | null = null;
    
    // Extract title
    if (titleMatch && titleMatch[1]) {
      visitTitle = titleMatch[1].trim();
    } else {
      // Try to extract from filename
      const filename = path.basename(filePath, path.extname(filePath));
      if (filename.includes('_')) {
        // Format like "GP_Dr_Kennard_Jan_17_2025.pdf"
        visitTitle = `Office Visit - ${filename.split('_').slice(-3).join(' ')}`;
      } else {
        visitTitle = `Office Visit - ${filename}`;
      }
    }
    
    // Extract date
    if (dateMatch && dateMatch[1]) {
      visitDate = new Date(dateMatch[1]);
    } else {
      // Try to extract from filename
      const fileNameDateMatch = path.basename(filePath).match(/(\d{1,2})[-_](\d{1,2})[-_](\d{2,4})/);
      if (fileNameDateMatch) {
        const year = fileNameDateMatch[3].length === 2 ? '20' + fileNameDateMatch[3] : fileNameDateMatch[3];
        const month = fileNameDateMatch[1].padStart(2, '0');
        const day = fileNameDateMatch[2].padStart(2, '0');
        visitDate = new Date(`${year}-${month}-${day}`);
      } else {
        // Try to extract month name from filename
        const monthNameMatch = path.basename(filePath).match(/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-_](\d{1,2})[-_](\d{2,4})/i);
        if (monthNameMatch) {
          const monthMap: { [key: string]: string } = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
            'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
          };
          
          const month = monthMap[monthNameMatch[1].toLowerCase().substring(0, 3)];
          const day = monthNameMatch[2].padStart(2, '0');
          const year = monthNameMatch[3].length === 2 ? '20' + monthNameMatch[3] : monthNameMatch[3];
          
          visitDate = new Date(`${year}-${month}-${day}`);
        }
      }
      
      // If still no date, check parent directory (if it's a year)
      if (!visitDate) {
        const parentDir = path.basename(path.dirname(filePath));
        if (/^(19|20)\d{2}$/.test(parentDir)) {
          visitDate = new Date(`${parentDir}-01-01`);
        } else {
          // Last resort, use current date
          visitDate = new Date();
        }
      }
    }
    
    // Extract provider and location
    const providerMatch = content.match(/(?:Provider|Doctor|Physician|Attended By):\s*([^\n]+)/i);
    const locationMatch = content.match(/(?:Location|Facility|Clinic):\s*([^\n]+)/i);
    
    // Extract diagnoses - look for Assessment and Plan section
    let diagnoses: string[] = [];
    
    // Try different patterns to extract diagnoses
    const diagnosisPatterns = [
      /(?:Assessment and Plan|Assessment|Impression|Diagnosis|Diagnoses):\s*([^\n]+(?:\n(?!\n)[^\n]+)*)/i,
      /(?:Problems|Problem List):\s*([^\n]+(?:\n(?!\n)[^\n]+)*)/i
    ];
    
    for (const pattern of diagnosisPatterns) {
      const match = content.match(pattern);
      if (match && match[1]) {
        // Split by numbered items or by lines
        diagnoses = match[1]
          .split(/\n|(?:\d+\.\s)/)
          .map(item => item.trim())
          .filter(item => item.length > 2);
        
        if (diagnoses.length > 0) {
          break;
        }
      }
    }
    
    // Create visit object
    const visit = {
      title: visitTitle,
      date: visitDate.toISOString(),
      provider: providerMatch ? providerMatch[1].trim() : '',
      location: locationMatch ? locationMatch[1].trim() : '',
      diagnosis: diagnoses,
      notes: content.substring(0, Math.min(content.length, 5000)), // Limit to first 5000 chars
      visit_type: 'Office Visit',
      source_file: path.basename(filePath)
    };
    
    visits.push(visit);
    console.log(`  Extracted visit details: ${visit.title}`);
  }
  
  return visits;
}

// Main function
function extractData() {
  console.log('===== Atrium Health PDF Data Extractor =====');
  console.log('This script will extract structured data from your Atrium Health PDFs.\n');
  
  // Create extracted data directory if it doesn't exist
  ensureDirectoryExists(extractedDataDir);
  
  // Process lab results
  console.log('Processing lab result PDFs...');
  const labResults = processLabResults();
  
  // Process visits
  console.log('\nProcessing visit/appointment PDFs...');
  const visits = processVisits();
  
  // Output the results
  const labResultsOutputFile = path.join(extractedDataDir, 'lab-results.json');
  const visitsOutputFile = path.join(extractedDataDir, 'visits.json');
  
  fs.writeFileSync(labResultsOutputFile, JSON.stringify(labResults, null, 2));
  fs.writeFileSync(visitsOutputFile, JSON.stringify(visits, null, 2));
  
  console.log(`\nExtracted ${labResults.length} lab results saved to: ${labResultsOutputFile}`);
  console.log(`Extracted ${visits.length} visit details saved to: ${visitsOutputFile}`);
  
  console.log('\nNext steps:');
  console.log('1. Review the extracted data in the JSON files');
  console.log('2. Run import-health-data.ts to import the data to your database');
}

// Run the extraction
extractData(); 