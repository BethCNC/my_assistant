import path from 'path';
import fs from 'fs';
import { execSync } from 'child_process';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import readline from 'readline';
import type { Database } from '../lib/supabase/database.types';
import * as glob from 'glob';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string;

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
      // If pdftotext fails, try a different approach
      console.log(`Note: pdftotext not available for ${path.basename(filePath)}. Install via 'brew install poppler' for better results.`);
      
      // On MacOS, try using textutil as a fallback
      try {
        const tempFile = path.join(process.cwd(), 'temp_pdf_text.txt');
        execSync(`textutil -convert txt -stdout "${filePath}" > "${tempFile}"`, { encoding: 'utf-8' });
        const content = fs.readFileSync(tempFile, 'utf-8');
        fs.unlinkSync(tempFile);
        return content;
      } catch (e2) {
        console.log(`Unable to extract text content from PDF. Please install pdftotext.`);
        return '';
      }
    }
  } catch (error) {
    console.error(`Error extracting content from ${filePath}: ${error}`);
    return '';
  }
}

// Extract date from string in various formats
function extractDate(text: string): Date | null {
  // Common date formats in medical records
  const datePatterns = [
    /(\d{1,2})[-\/](\d{1,2})[-\/](\d{2,4})/,         // MM/DD/YYYY or MM-DD-YYYY
    /(\w+)\s+(\d{1,2}),?\s+(\d{4})/,                 // Month DD, YYYY
    /(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})/,           // YYYY/MM/DD or YYYY-MM-DD
    /(\d{1,2})[-\/](\w+)[-\/](\d{4})/,               // DD/MMM/YYYY
  ];
  
  for (const pattern of datePatterns) {
    const match = text.match(pattern);
    if (match) {
      try {
        // Try to parse the date based on the pattern
        const dateStr = match[0];
        const date = new Date(dateStr);
        if (!isNaN(date.getTime())) {
          return date;
        }
      } catch (e) {
        // Continue to next pattern if parsing fails
      }
    }
  }
  
  return null;
}

// Extract lab test results from PDF content
function extractLabResults(content: string, fileName: string) {
  const labResultData: any[] = [];
  const labResultLines = content.split('\n');
  
  // Try to extract collection date
  let collectionDate = null;
  
  // Look for collection date in the first 20 lines
  for (let i = 0; i < Math.min(20, labResultLines.length); i++) {
    const line = labResultLines[i];
    if (line.includes('Collected on')) {
      const dateText = line.split('Collected on')[1]?.trim() || '';
      collectionDate = extractDate(dateText);
      break;
    }
  }
  
  // If we couldn't find a collection date, try to extract from filename
  if (!collectionDate) {
    collectionDate = extractDate(fileName);
  }
  
  // Pattern to identify "Normal range" lines
  const normalRangePattern = /Normal range:\s*([\d\.-]+)\s*-\s*([\d\.-]+)\s*(\w+\/?\w*)/;
  
  // Process all lines for lab results
  for (let i = 0; i < labResultLines.length; i++) {
    const line = labResultLines[i].trim();
    
    // Look for lines with "Normal range:" which indicate a lab test
    const rangeMatch = line.match(normalRangePattern);
    
    if (rangeMatch) {
      // Found a normal range line, now extract the test name, value and other info
      const [_, lowerBound, upperBound, unit] = rangeMatch;
      const referenceRange = `${lowerBound} - ${upperBound}`;
      
      // Test name is usually 1-3 lines before the normal range line
      let testName = '';
      for (let j = 1; j <= 3; j++) {
        if (i - j >= 0 && labResultLines[i - j].trim() !== '') {
          const potentialName = labResultLines[i - j].trim();
          // Exclude lines that look like they're not test names
          if (!potentialName.includes('Normal range:') && 
              !potentialName.includes(':') && 
              !potentialName.match(/^\d+(\.\d+)?$/) &&
              !potentialName.includes('Results')) {
            testName = potentialName;
            break;
          }
        }
      }
      
      // Value is usually 1-3 lines after the normal range line
      let resultValue = '';
      for (let j = 1; j <= 3; j++) {
        if (i + j < labResultLines.length && labResultLines[i + j].trim() !== '') {
          const potentialValue = labResultLines[i + j].trim();
          // Look for a line that contains just a number
          if (potentialValue.match(/^[\d\.]+$/) && !potentialValue.includes('Normal range:')) {
            resultValue = potentialValue;
            break;
          }
        }
      }
      
      // If we found a test name and result value, add it to our data
      if (testName && resultValue) {
        // Determine if result is abnormal based on reference range
        const isAbnormal = determineAbnormal(resultValue, referenceRange);
        
        labResultData.push({
          test_name: testName,
          result: resultValue,
          unit: unit || '',
          reference_range: referenceRange,
          is_abnormal: isAbnormal,
          date: collectionDate,
          category: determineTestCategory(testName),
          notes: extractTestNotes(labResultLines, i),
        });
      }
    }
  }
  
  // Look for special result formats (especially for imaging or narrative reports)
  if (labResultData.length === 0 && content.includes('Impression')) {
    // This might be an imaging report
    const impression = extractImpression(labResultLines);
    const narrative = extractNarrative(labResultLines);
    
    if (impression || narrative) {
      // Create a result entry for this imaging report
      const testName = extractTestName(labResultLines) || fileName.replace('.pdf', '');
      
      labResultData.push({
        test_name: testName,
        result: impression || 'See narrative',
        unit: '',
        reference_range: '',
        is_abnormal: false,
        date: collectionDate,
        category: 'Imaging',
        notes: narrative,
      });
    }
  }
  
  return labResultData;
}

// Extract test name from PDF content 
function extractTestName(lines: string[]): string {
  // Look for a test name in the first 10 lines
  for (let i = 0; i < Math.min(10, lines.length); i++) {
    const line = lines[i].trim();
    // Skip lines with common header information
    if (line.includes('Name:') || line.includes('DOB:') || line.includes('MRN:') || 
        line.includes('PCP:') || line.includes('Collected on') || line === '') {
      continue;
    }
    
    // This is likely the test name
    return line;
  }
  return '';
}

// Extract impression section from imaging reports
function extractImpression(lines: string[]): string {
  const impressions = [];
  let inImpressionSection = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line === 'Impression' || line.includes('IMPRESSION:')) {
      inImpressionSection = true;
      continue;
    }
    
    if (inImpressionSection) {
      // End of impression section
      if (line === '' || line.includes('Ordering provider:') || line.includes('Reading physician:')) {
        break;
      }
      
      impressions.push(line);
    }
  }
  
  return impressions.join(' ');
}

// Extract narrative section from reports
function extractNarrative(lines: string[]): string {
  const narrative = [];
  let inNarrativeSection = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line === 'Narrative' || line.includes('NARRATIVE:') || line.includes('FINDINGS:')) {
      inNarrativeSection = true;
      continue;
    }
    
    if (inNarrativeSection) {
      // End of narrative section
      if (line.includes('Ordering provider:') || line.includes('Reading physician:')) {
        break;
      }
      
      if (line !== '') {
        narrative.push(line);
      }
    }
  }
  
  return narrative.join(' ');
}

// Determine if a result is abnormal based on reference range
function determineAbnormal(result: string, referenceRange: string): boolean {
  // Parse numeric result
  const numericResult = parseFloat(result);
  
  // If can't parse as number, return false
  if (isNaN(numericResult)) {
    return false;
  }
  
  // Parse reference range 
  // Common patterns: "3.5-5.0", "<5.0", ">10.0", "Negative"
  if (referenceRange.includes('-')) {
    // Range like "3.5-5.0"
    const [min, max] = referenceRange.split('-').map(s => parseFloat(s.trim()));
    return numericResult < min || numericResult > max;
  } else if (referenceRange.includes('<')) {
    // Upper limit like "<5.0"
    const max = parseFloat(referenceRange.replace('<', '').trim());
    return numericResult >= max;
  } else if (referenceRange.includes('>')) {
    // Lower limit like ">10.0"
    const min = parseFloat(referenceRange.replace('>', '').trim());
    return numericResult <= min;
  }
  
  // Default to not abnormal if we can't determine
  return false;
}

// Determine test category based on test name
function determineTestCategory(testName: string): string {
  const lowerName = testName.toLowerCase();
  
  if (lowerName.includes('glucose') || lowerName.includes('a1c') || lowerName.includes('insulin')) {
    return 'Blood Sugar';
  } else if (lowerName.includes('cholesterol') || lowerName.includes('ldl') || lowerName.includes('hdl') || lowerName.includes('triglyceride')) {
    return 'Lipids';
  } else if (lowerName.includes('tsh') || lowerName.includes('t3') || lowerName.includes('t4') || lowerName.includes('thyroid')) {
    return 'Thyroid';
  } else if (lowerName.includes('wbc') || lowerName.includes('rbc') || lowerName.includes('hemoglobin') || lowerName.includes('hematocrit') || lowerName.includes('platelet')) {
    return 'Complete Blood Count';
  } else if (lowerName.includes('sodium') || lowerName.includes('potassium') || lowerName.includes('chloride') || lowerName.includes('calcium') || lowerName.includes('magnesium')) {
    return 'Electrolytes';
  } else if (lowerName.includes('alt') || lowerName.includes('ast') || lowerName.includes('bilirubin') || lowerName.includes('alkaline phosphatase')) {
    return 'Liver Function';
  } else if (lowerName.includes('creatinine') || lowerName.includes('bun') || lowerName.includes('egfr')) {
    return 'Kidney Function';
  }
  
  return 'General';
}

// Extract additional notes about the test
function extractTestNotes(lines: string[], lineIndex: number): string {
  // Check the next few lines for notes
  const notes = [];
  let i = lineIndex + 1;
  
  while (i < Math.min(lineIndex + 5, lines.length)) {
    const line = lines[i].trim();
    
    // If the line doesn't look like a new test result, consider it a note
    if (line && !line.includes(':') && !line.match(/^\d/) && line !== 'Normal' && line !== 'Abnormal') {
      notes.push(line);
    } else if (line.includes('Note:')) {
      notes.push(line);
    } else if (line.includes('Comment:')) {
      notes.push(line);
    } else {
      // Stop if we encounter what looks like a new test
      break;
    }
    
    i++;
  }
  
  return notes.join(' ');
}

// Extract appointment/visit details from PDF content
function extractVisitDetails(content: string, fileName: string) {
  const visitData: any = {
    title: '',
    date: null,
    provider: '',
    location: '',
    diagnosis: [],
    notes: '',
    visit_type: '',
  };
  
  const visitLines = content.split('\n');
  
  // Extract visit info from the first few lines where it's typically found
  for (let i = 0; i < Math.min(20, visitLines.length); i++) {
    const line = visitLines[i].trim();
    
    // Visit title with date and type
    if (line.startsWith('Office Visit') || line.includes('Visit -')) {
      visitData.title = line;
      // Extract the date
      const dateMatch = line.match(/(\w+)\s+(\d{1,2}),\s+(\d{4})/);
      if (dateMatch) {
        const dateStr = dateMatch[0];
        visitData.date = new Date(dateStr);
      }
      continue;
    }
    
    // Provider and location line
    if (line.startsWith('with') && line.includes('at')) {
      const parts = line.split('at');
      if (parts.length === 2) {
        // Extract provider
        const providerMatch = parts[0].match(/with\s+(.*)/);
        if (providerMatch) {
          visitData.provider = providerMatch[1].trim();
        }
        // Extract location
        visitData.location = parts[1].trim();
      }
      continue;
    }
  }
  
  // If no title was found, try to extract it from other patterns
  if (!visitData.title) {
    // Try to find a line that looks like a visit type
    for (let i = 0; i < Math.min(30, visitLines.length); i++) {
      const line = visitLines[i].trim();
      
      if (line.includes('Progress Notes') || line.includes('Office Visit') || 
          line.includes('Follow-up Visit')) {
        visitData.title = line;
        break;
      }
    }
    
    // If still no title, use the filename
    if (!visitData.title) {
      visitData.title = path.basename(fileName, '.pdf').replace('MyAtriumHealth - ', '');
    }
  }
  
  // Extract visit date if not found already
  if (!visitData.date) {
    for (let i = 0; i < visitLines.length; i++) {
      const line = visitLines[i].trim();
      
      // Look for date patterns in the first 30 lines
      if (i < 30 && (line.includes('Date of Service:') || line.includes('Visit Date:'))) {
        const dateText = line.split(':')[1]?.trim() || '';
        visitData.date = extractDate(dateText);
        if (visitData.date) break;
      }
      
      // Look for a line with just a date in MM/DD/YYYY format
      const dateMatch = line.match(/^\d{1,2}\/\d{1,2}\/\d{4}$/);
      if (dateMatch && i < 50) {
        visitData.date = new Date(line);
        if (visitData.date) break;
      }
    }
  }
  
  // Extract visit type if not already in title
  if (!visitData.visit_type && visitData.title) {
    if (visitData.title.includes('Office Visit')) {
      visitData.visit_type = 'Office Visit';
    } else if (visitData.title.includes('Follow-up')) {
      visitData.visit_type = 'Follow-up Visit';
    } else if (visitData.title.includes('Consult')) {
      visitData.visit_type = 'Consultation';
    } else if (visitData.title.includes('Emergency')) {
      visitData.visit_type = 'Emergency Visit';
    } else if (visitData.title.includes('Surgery')) {
      visitData.visit_type = 'Surgery';
    } else if (visitData.title.includes('Procedure')) {
      visitData.visit_type = 'Procedure';
    } else if (visitData.title.includes('Telehealth')) {
      visitData.visit_type = 'Telehealth Visit';
    } else {
      visitData.visit_type = 'Office Visit'; // Default
    }
  }
  
  // Extract diagnoses
  const diagnoses = [];
  let inDiagnosisSection = false;
  
  for (let i = 0; i < visitLines.length; i++) {
    const line = visitLines[i].trim();
    
    // Look for diagnosis sections
    if ((line === 'Diagnoses:' || line === 'Diagnosis:' || line === 'Assessment:' || 
         line.includes('Impression:') || line.includes('Assessment and Plan:')) && !inDiagnosisSection) {
      inDiagnosisSection = true;
      continue;
    }
    
    // Collect diagnoses
    if (inDiagnosisSection) {
      // End diagnosis section at these markers
      if (line === 'Plan:' || line === 'Treatment Plan:' || line === '' || 
          line.includes('Medications:') || line.includes('Orders:')) {
        inDiagnosisSection = false;
        continue;
      }
      
      // Skip numbered lines with just periods (often formatting)
      if (!line.match(/^\d+\.$/) && line.length > 0) {
        // If line starts with a number, it's likely a diagnosis
        if (line.match(/^\d+\./) || line.match(/^[A-Z][0-9]+\./)) {
          diagnoses.push(line.replace(/^\d+\./, '').trim());
        } else {
          diagnoses.push(line);
        }
      }
    }
  }
  
  // If no formal diagnoses found, look for "Impression" section which often contains diagnoses
  if (diagnoses.length === 0) {
    let inImpressionSection = false;
    
    for (let i = 0; i < visitLines.length; i++) {
      const line = visitLines[i].trim();
      
      if (line === 'Impression:' || line === 'IMPRESSION:') {
        inImpressionSection = true;
        continue;
      }
      
      if (inImpressionSection && line.length > 0) {
        if (line.match(/^\d+\./) || line.match(/^[A-Z][0-9]+\./)) {
          // Lines that start with a number followed by a period
          diagnoses.push(line.replace(/^\d+\./, '').trim());
        } else if (!line.includes('Electronically signed')) {
          diagnoses.push(line);
        }
        
        // End at common section markers
        if (line === '' || line.includes('Electronically signed')) {
          inImpressionSection = false;
        }
      }
    }
  }
  
  visitData.diagnosis = diagnoses;
  
  // Extract provider if not found earlier
  if (!visitData.provider) {
    for (let i = 0; i < visitLines.length; i++) {
      const line = visitLines[i].trim();
      
      if (line.includes('Provider:') || line.includes('Doctor:') || 
          line.includes('Physician:') || line.includes('Electronically signed by')) {
        const providerMatch = line.match(/:\s*([^,]+),?\s*M\.?D\.?/);
        if (providerMatch) {
          visitData.provider = providerMatch[1].trim();
          break;
        } else if (line.includes('Electronically signed by')) {
          const esMatch = line.match(/Electronically signed by\s+([^,]+)/);
          if (esMatch) {
            visitData.provider = esMatch[1].trim();
            break;
          }
        }
      }
    }
  }
  
  // Extract notes from specific sections
  const notes = [];
  let inNotesSection = false;
  
  for (let i = 0; i < visitLines.length; i++) {
    const line = visitLines[i].trim();
    
    // Start notes section
    if (line === 'Subjective:' || line === 'HPI:' || line === 'History of Present Illness' || 
        line === 'Plan:' || line === 'Notes:' || line === 'Comments:' || 
        line === 'Treatment Plan:' || line === 'Recommendations:') {
      inNotesSection = true;
      continue;
    }
    
    // Collect notes
    if (inNotesSection && line.length > 0) {
      // End notes at common section markers
      if (line === 'Assessment:' || line === 'Diagnosis:' || line === 'Orders:' ||
          line === 'Electronically signed' || line.includes('Electronically signed by')) {
        inNotesSection = false;
        continue;
      }
      
      notes.push(line);
    }
  }
  
  // If we didn't find structured notes, try to get any content past the first few sections
  if (notes.length === 0) {
    let contentStart = false;
    
    for (let i = 10; i < visitLines.length; i++) {
      const line = visitLines[i].trim();
      
      // Skip header parts and empty lines
      if (i < 15 || line === '') {
        continue;
      }
      
      // Start capturing after we find a non-empty line past the headers
      if (!contentStart && line.length > 0 && 
          !line.includes('Name:') && !line.includes('DOB:') && 
          !line.includes('Progress Notes') && !line.includes('Office Visit')) {
        contentStart = true;
      }
      
      if (contentStart && line.length > 0 && !line.includes('MyChart® licensed from Epic')) {
        notes.push(line);
      }
    }
  }
  
  visitData.notes = notes.join(' ');
  
  return visitData;
}

// Process lab results
function processLabResults(): any[] {
  const results: any[] = [];
  
  // Get all PDF files in the lab-results directory and its subdirectories
  const labResultFiles = glob.sync('**/*.pdf', { 
    cwd: labResultsDir, 
    absolute: true,
    nocase: true,
    ignore: ['**/node_modules/**'] 
  });

  console.log(`Found ${labResultFiles.length} lab result PDFs to process.`);
  
  for (const filePath of labResultFiles) {
    console.log(`\nExtracting data from: ${path.basename(filePath)}`);
    
    const content = getPdfText(filePath);
    if (!content) {
      console.log(`  No content extracted from file.`);
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
        }
      }
      
      // If still no date, use current date
      if (!date) {
        date = new Date();
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
function processVisits(): any[] {
  const visits: any[] = [];
  
  // Get all PDF files in the appointments directory and its subdirectories
  const visitFiles = glob.sync('**/*.pdf', { 
    cwd: appointmentsDir, 
    absolute: true,
    nocase: true,
    ignore: ['**/node_modules/**'] 
  });
  
  console.log(`Found ${visitFiles.length} visit/appointment PDFs to process.`);
  
  for (const filePath of visitFiles) {
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
    
    // If that didn't work, try extracting numbered items after Assessment section
    if (diagnoses.length === 0) {
      const assessmentMatch = content.match(/(?:Assessment|Assessment and Plan|Impression|Diagnosis|Diagnoses)(?:[\s\S]*?)(\d+\.[\s\S]*?)(?:Plan|Follow-up|Patient Instructions|Electronically signed|$)/i);
      
      if (assessmentMatch && assessmentMatch[1]) {
        diagnoses = assessmentMatch[1]
          .split(/\d+\.\s/)
          .map(item => item.trim())
          .filter(item => item.length > 2);
      }
    }
    
    // If still no diagnoses, try to find lines with typical diagnosis patterns
    if (diagnoses.length === 0) {
      // Look for text that appear to be diagnoses (like "Hypertension (Primary)")
      const diagnosisLines = content.match(/(?:^|\n)([A-Z][a-z]+(?: [a-z]+)*(?: \([^)]+\))?)(?:\n|$)/gm);
      
      if (diagnosisLines) {
        diagnoses = diagnosisLines
          .map(line => line.trim())
          .filter(line => 
            line.length > 5 && 
            !line.includes('Provider') && 
            !line.includes('Patient') && 
            !line.includes('Doctor') &&
            !line.includes('Visit') &&
            !line.includes('Date')
          );
      }
    }
    
    // Create visit object
    const visit = {
      title: visitTitle,
      date: visitDate.toISOString(),
      provider: providerMatch ? providerMatch[1].trim() : '',
      location: locationMatch ? locationMatch[1].trim() : '',
      diagnosis: diagnoses,
      notes: content.substring(0, Math.min(content.length, 10000)), // Limit to 10000 chars
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
  
  console.log('\nWould you like to import this data to your Supabase database? (y/n): ');
}

// Run the extraction
extractData(); 