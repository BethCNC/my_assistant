import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';
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

// Define output directory
const OUTPUT_DIR = path.join(process.cwd(), 'data', 'consolidated');

// Ensure output directories exist
const DIRECTORIES = [
  OUTPUT_DIR,
  path.join(OUTPUT_DIR, 'lab_results'),
  path.join(OUTPUT_DIR, 'appointments'),
  path.join(OUTPUT_DIR, 'conditions'),
  path.join(OUTPUT_DIR, 'providers'),
  path.join(OUTPUT_DIR, 'imaging'),
  path.join(OUTPUT_DIR, 'notes'),
  path.join(OUTPUT_DIR, 'medications'),
  path.join(OUTPUT_DIR, 'symptoms'),
];

DIRECTORIES.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Helper function to save data to JSON file
function saveToJson(filename: string, data: any) {
  const filePath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  console.log(`Saved ${filePath}`);
}

// Export lab results
async function exportLabResults() {
  console.log('Exporting lab results...');
  try {
    const { data, error } = await supabase
      .from('lab_results')
      .select('*');

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log('No lab results found');
      return;
    }
    
    console.log(`Found ${data.length} lab results`);
    
    // Save all lab results to a single file
    saveToJson('lab_results.json', data);
    
    // Save each lab result to its own file
    data.forEach((labResult, index) => {
      const date = labResult.date ? new Date(labResult.date).toISOString().split('T')[0] : 'unknown-date';
      const testName = labResult.test_name?.replace(/\s+/g, '_').toLowerCase() || 'unknown-test';
      const filename = `lab_results/${date}-${testName}-${index}.json`;
      saveToJson(filename, labResult);
    });
    
  } catch (error) {
    console.error('Error exporting lab results:', error);
  }
}

// Export medical events (appointments)
async function exportMedicalEvents() {
  console.log('Exporting medical events...');
  try {
    const { data, error } = await supabase
      .from('medical_events')
      .select('*');

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log('No medical events found');
      return;
    }
    
    console.log(`Found ${data.length} medical events`);
    
    // Save all medical events to a single file
    saveToJson('medical_events.json', data);
    
    // Group events by type
    const appointments = data.filter(event => 
      event.event_type === 'appointment' || 
      event.title?.toLowerCase().includes('visit') || 
      event.title?.toLowerCase().includes('appointment')
    );
    
    const imaging = data.filter(event => 
      event.event_type === 'imaging' || 
      event.title?.toLowerCase().includes('x-ray') || 
      event.title?.toLowerCase().includes('mri') || 
      event.title?.toLowerCase().includes('ct scan') ||
      event.title?.toLowerCase().includes('ultrasound')
    );
    
    // Save appointments
    appointments.forEach((appointment, index) => {
      const date = appointment.date ? new Date(appointment.date).toISOString().split('T')[0] : 'unknown-date';
      const title = appointment.title?.replace(/\s+/g, '_').toLowerCase() || 'unknown-appointment';
      const filename = `appointments/${date}-${title}-${index}.json`;
      saveToJson(filename, appointment);
    });
    
    // Save imaging records
    imaging.forEach((image, index) => {
      const date = image.date ? new Date(image.date).toISOString().split('T')[0] : 'unknown-date';
      const title = image.title?.replace(/\s+/g, '_').toLowerCase() || 'unknown-imaging';
      const filename = `imaging/${date}-${title}-${index}.json`;
      saveToJson(filename, image);
    });
    
  } catch (error) {
    console.error('Error exporting medical events:', error);
  }
}

// Export conditions (diagnoses)
async function exportConditions() {
  console.log('Exporting conditions...');
  try {
    const { data, error } = await supabase
      .from('conditions')
      .select('*');

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log('No conditions found');
      return;
    }
    
    console.log(`Found ${data.length} conditions`);
    
    // Save all conditions to a single file
    saveToJson('conditions.json', data);
    
    // Save each condition to its own file
    data.forEach((condition, index) => {
      const name = condition.name?.replace(/\s+/g, '_').toLowerCase() || 'unknown-condition';
      const filename = `conditions/${name}-${index}.json`;
      saveToJson(filename, condition);
    });
    
  } catch (error) {
    console.error('Error exporting conditions:', error);
  }
}

// Export providers
async function exportProviders() {
  console.log('Exporting providers...');
  try {
    const { data, error } = await supabase
      .from('providers')
      .select('*');

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log('No providers found');
      return;
    }
    
    console.log(`Found ${data.length} providers`);
    
    // Save all providers to a single file
    saveToJson('providers.json', data);
    
    // Save each provider to its own file
    data.forEach((provider, index) => {
      const name = provider.name?.replace(/\s+/g, '_').toLowerCase() || 'unknown-provider';
      const filename = `providers/${name}-${index}.json`;
      saveToJson(filename, provider);
    });
    
  } catch (error) {
    console.error('Error exporting providers:', error);
  }
}

// Export medications
async function exportMedications() {
  console.log('Exporting medications...');
  try {
    const { data, error } = await supabase
      .from('medications')
      .select('*');

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log('No medications found');
      return 0;
    }
    
    console.log(`Found ${data.length} medications`);
    
    // Save all medications to a single file
    saveToJson('medications.json', data);
    
    // Save each medication to its own file
    data.forEach((medication, index) => {
      const name = medication.name?.replace(/\s+/g, '_').toLowerCase() || 'unknown-medication';
      const filename = `medications/${name}-${index}.json`;
      saveToJson(filename, medication);
    });
    
    return data.length;
    
  } catch (error) {
    console.error('Error exporting medications:', error);
    return 0;
  }
}

// Export symptoms
async function exportSymptoms() {
  console.log('Exporting symptoms...');
  try {
    const { data, error } = await supabase
      .from('symptoms')
      .select('*');

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log('No symptoms found');
      return 0;
    }
    
    console.log(`Found ${data.length} symptoms`);
    
    // Save all symptoms to a single file
    saveToJson('symptoms.json', data);
    
    // Save each symptom to its own file
    data.forEach((symptom, index) => {
      const name = symptom.name?.replace(/\s+/g, '_').toLowerCase() || 'unknown-symptom';
      const filename = `symptoms/${name}-${index}.json`;
      saveToJson(filename, symptom);
    });
    
    return data.length;
    
  } catch (error) {
    console.error('Error exporting symptoms:', error);
    return 0;
  }
}

// Export text files from novant_summary
function exportNovantFiles() {
  console.log('Exporting Novant Health text files...');
  const novantDir = path.join(process.cwd(), 'data', 'novant_summary', 'Novant_Health');
  
  if (!fs.existsSync(novantDir)) {
    console.log('Novant_Health directory not found');
    return;
  }
  
  // Get all text files
  const files = fs.readdirSync(novantDir)
    .filter(file => file.endsWith('.txt'));
  
  console.log(`Found ${files.length} text files in Novant_Health directory`);
  
  // Create a summary of all text files
  const textFileContents: any = {};
  
  files.forEach(file => {
    try {
      const filePath = path.join(novantDir, file);
      const content = fs.readFileSync(filePath, 'utf-8');
      
      // Determine category based on filename
      let category = 'notes';
      if (file.includes('XR_') || file.includes('MRI_') || file.includes('CT_')) {
        category = 'imaging';
      } else if (file.includes('LAB_')) {
        category = 'lab_results';
      }
      
      // Extract date from filename (format: YYYY-MM-DD)
      const dateMatch = file.match(/(\d{4}-\d{2}-\d{2})/);
      const date = dateMatch ? dateMatch[1] : 'unknown-date';
      
      // Clean up name
      const name = file
        .replace(/\.txt$/, '')
        .replace(/\d{4}-\d{2}-\d{2}T\d{2}_\d{2}_\d{2}Z-/, '')
        .replace(/_/g, ' ');
      
      // Create a JSON representation
      const jsonData = {
        source: 'Novant_Health',
        filename: file,
        name,
        date,
        content
      };
      
      // Save to appropriate category
      const outputFilename = `${category}/${date}-${file.replace('.txt', '.json')}`;
      saveToJson(outputFilename, jsonData);
      
      // Add to summary
      textFileContents[file] = {
        category,
        date,
        name,
        content_length: content.length
      };
    } catch (error) {
      console.error(`Error processing ${file}:`, error);
    }
  });
  
  // Save summary
  saveToJson('novant_text_files_summary.json', textFileContents);
}

// Export text files from atrium_summary
function exportAtriumFiles() {
  console.log('Exporting Atrium Health files...');
  const atriumDir = path.join(process.cwd(), 'data', 'atrium_summary', 'Atrium_HealthSummary_Apr_10_2025');
  
  if (!fs.existsSync(atriumDir)) {
    console.log('Atrium_HealthSummary directory not found');
    return;
  }
  
  // Find the IHE_XDM directory
  const iheDir = path.join(atriumDir, 'IHE_XDM');
  if (!fs.existsSync(iheDir)) {
    console.log('IHE_XDM directory not found in Atrium summary');
    return;
  }
  
  // Recursively process patient directories
  const patientDirs = fs.readdirSync(iheDir);
  console.log(`Found ${patientDirs.length} patient directories in IHE_XDM`);
  
  // Process each patient directory
  patientDirs.forEach(patientDir => {
    const fullPatientDir = path.join(iheDir, patientDir);
    
    if (fs.statSync(fullPatientDir).isDirectory()) {
      // Get all XML files in patient directory
      const xmlFiles = fs.readdirSync(fullPatientDir)
        .filter(file => file.endsWith('.XML') && file !== 'METADATA.XML');
      
      console.log(`Found ${xmlFiles.length} clinical document XML files for ${patientDir}`);
      
      // Process and save each XML file
      xmlFiles.forEach(xmlFile => {
        try {
          const filePath = path.join(fullPatientDir, xmlFile);
          const content = fs.readFileSync(filePath, 'utf-8');
          
          // Extract document type and date (basic extraction)
          let documentType = 'unknown';
          let date = 'unknown-date';
          
          // Very basic XML parsing - for a full solution, use an XML parser
          const titleMatch = content.match(/<title>(.*?)<\/title>/);
          if (titleMatch) {
            documentType = titleMatch[1];
          }
          
          const dateMatch = content.match(/(\d{4}-\d{2}-\d{2})/);
          if (dateMatch) {
            date = dateMatch[1];
          }
          
          // Determine category
          let category = 'notes';
          const docLower = documentType.toLowerCase();
          if (docLower.includes('lab') || docLower.includes('test')) {
            category = 'lab_results';
          } else if (docLower.includes('x-ray') || docLower.includes('mri') || 
                     docLower.includes('ct') || docLower.includes('ultrasound') ||
                     docLower.includes('imaging')) {
            category = 'imaging';
          } else if (docLower.includes('visit') || docLower.includes('encounter') ||
                     docLower.includes('appointment')) {
            category = 'appointments';
          }
          
          // Create a JSON representation
          const jsonData = {
            source: 'Atrium_Health',
            filename: xmlFile,
            name: documentType,
            date,
            content
          };
          
          // Save to appropriate category
          const sanitizedName = documentType.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
          const outputFilename = `${category}/${date}-${sanitizedName}.json`;
          saveToJson(outputFilename, jsonData);
        } catch (error) {
          console.error(`Error processing ${xmlFile}:`, error);
        }
      });
    }
  });
  
  // Check for PDF files
  const pdfFiles = [];
  function findPdfFiles(dir: string) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const fullPath = path.join(dir, file);
      if (fs.statSync(fullPath).isDirectory()) {
        findPdfFiles(fullPath);
      } else if (file.endsWith('.PDF') || file.endsWith('.pdf')) {
        pdfFiles.push(fullPath);
      }
    });
  }
  
  findPdfFiles(atriumDir);
  console.log(`Found ${pdfFiles.length} PDF files in Atrium Health directory`);
  
  // Save PDF file paths
  saveToJson('atrium_pdf_files.json', pdfFiles);
}

// Main export function
async function exportAllData() {
  console.log('Starting export of all health data...');
  
  // Export from Supabase
  await exportLabResults();
  await exportMedicalEvents();
  await exportConditions();
  await exportProviders();
  const medicationCount = await exportMedications();
  const symptomCount = await exportSymptoms();
  
  // Export from text files
  exportNovantFiles();
  exportAtriumFiles();
  
  // Generate a data summary
  const summary = {
    export_date: new Date().toISOString(),
    data_sources: [
      'Supabase database',
      'Novant Health text files',
      'Atrium Health XML files'
    ],
    data_counts: {
      lab_results: fs.readdirSync(path.join(OUTPUT_DIR, 'lab_results')).length,
      appointments: fs.readdirSync(path.join(OUTPUT_DIR, 'appointments')).length,
      conditions: fs.readdirSync(path.join(OUTPUT_DIR, 'conditions')).length,
      providers: fs.readdirSync(path.join(OUTPUT_DIR, 'providers')).length,
      imaging: fs.readdirSync(path.join(OUTPUT_DIR, 'imaging')).length,
      notes: fs.readdirSync(path.join(OUTPUT_DIR, 'notes')).length,
      medications: medicationCount,
      symptoms: symptomCount
    },
    files_exported: fs.readdirSync(OUTPUT_DIR)
      .filter(file => file.endsWith('.json'))
      .length
  };
  
  saveToJson('data_summary.json', summary);
  
  console.log('-----------------------------------');
  console.log('Export complete! Summary:');
  console.log(`Lab Results: ${summary.data_counts.lab_results}`);
  console.log(`Appointments: ${summary.data_counts.appointments}`);
  console.log(`Conditions: ${summary.data_counts.conditions}`);
  console.log(`Providers: ${summary.data_counts.providers}`);
  console.log(`Imaging: ${summary.data_counts.imaging}`);
  console.log(`Notes: ${summary.data_counts.notes}`);
  console.log(`Medications: ${summary.data_counts.medications}`);
  console.log(`Symptoms: ${summary.data_counts.symptoms}`);
  console.log('-----------------------------------');
  console.log(`Total JSON files created: ${summary.files_exported}`);
  console.log(`All data exported to: ${OUTPUT_DIR}`);
  console.log('-----------------------------------');
}

// Run the export
exportAllData().catch(err => {
  console.error('Error during export:', err);
  process.exit(1);
}); 