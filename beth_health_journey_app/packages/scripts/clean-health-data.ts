import fs from 'fs';
import path from 'path';

interface LabResult {
  name: string;
  result: string;
  unit?: string;
  reference_range?: string;
  is_abnormal: boolean;
  date: string;
  category?: string;
  notes?: string;
  source_file: string;
}

interface Visit {
  title: string;
  date: string;
  provider: string;
  location: string;
  diagnosis: string[];
  notes: string;
  visit_type: string;
  source_file: string;
}

function cleanDiagnosis(diagnosis: string[]): string[] {
  return diagnosis.filter(d => {
    // Remove entries that are dates, orders, or headers
    return !d.match(/^\d+\/\d+\/\d+$/) && // Not a date
           !d.includes('Order:') &&      // Not an order
           !d.includes('Status:') &&     // Not a status
           !d.includes('Impression') &&  // Not an impression header
           !d.includes('DATE OF SERVICE') && // Not a service date header
           !d.includes('EXAM:') &&       // Not an exam header
           d.length >= 3                 // Not too short
  });
}

function extractProviderLocation(notes: string): { provider: string; location: string } {
  const provider = notes.match(/with ([^at]+) at (.+?)(\n|$)/);
  if (provider && provider.length > 2) {
    return {
      provider: provider[1].trim(),
      location: provider[2].trim()
    };
  }
  return { provider: '', location: '' };
}

async function cleanData() {
  // Read the data files
  const labResultsPath = path.join(process.cwd(), 'data/atrium-exports/extracted-data/lab-results.json');
  const visitsPath = path.join(process.cwd(), 'data/atrium-exports/extracted-data/visits.json');
  
  const labResults: LabResult[] = JSON.parse(fs.readFileSync(labResultsPath, 'utf-8'));
  const visits: Visit[] = JSON.parse(fs.readFileSync(visitsPath, 'utf-8'));

  // Clean visits data
  const cleanedVisits = visits.map(visit => {
    const { provider, location } = extractProviderLocation(visit.notes);
    return {
      ...visit,
      provider: visit.provider || provider,
      location: visit.location || location,
      diagnosis: cleanDiagnosis(visit.diagnosis)
    };
  });

  // Write cleaned data back to files
  const cleanedLabResultsPath = path.join(process.cwd(), 'data/atrium-exports/extracted-data/lab-results.clean.json');
  const cleanedVisitsPath = path.join(process.cwd(), 'data/atrium-exports/extracted-data/visits.clean.json');

  fs.writeFileSync(cleanedLabResultsPath, JSON.stringify(labResults, null, 2));
  fs.writeFileSync(cleanedVisitsPath, JSON.stringify(cleanedVisits, null, 2));

  console.log('Data cleaning complete!');
  console.log(`Cleaned lab results saved to: ${cleanedLabResultsPath}`);
  console.log(`Cleaned visits saved to: ${cleanedVisitsPath}`);
}

cleanData().catch(console.error); 