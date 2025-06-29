import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Define input directory
const DATA_DIR = path.join(process.cwd(), 'data', 'consolidated');
const OUTPUT_DIR = path.join(process.cwd(), 'data', 'analysis');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Helper function to load JSON data
function loadJson(filename: string) {
  try {
    const filePath = path.join(DATA_DIR, filename);
    if (!fs.existsSync(filePath)) {
      return null;
    }
    const data = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error loading ${filename}:`, error);
    return null;
  }
}

// Helper function to save analysis results
function saveAnalysis(filename: string, data: any) {
  const filePath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  console.log(`Saved analysis to ${filePath}`);
}

// Count files in a directory
function countFilesInDir(dirName: string) {
  const dirPath = path.join(DATA_DIR, dirName);
  if (!fs.existsSync(dirPath)) {
    return 0;
  }
  return fs.readdirSync(dirPath).filter(file => file.endsWith('.json')).length;
}

// Get all files from a directory
function getFilesFromDir(dirName: string) {
  const dirPath = path.join(DATA_DIR, dirName);
  if (!fs.existsSync(dirPath)) {
    return [];
  }
  
  return fs.readdirSync(dirPath)
    .filter(file => file.endsWith('.json'))
    .map(file => {
      try {
        const filePath = path.join(dirPath, file);
        const data = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(data);
      } catch (error) {
        console.error(`Error reading ${file}:`, error);
        return null;
      }
    })
    .filter(item => item !== null);
}

// Analyze lab results
function analyzeLabResults() {
  console.log('Analyzing lab results...');
  const labResults = getFilesFromDir('lab_results');
  
  if (labResults.length === 0) {
    console.log('No lab results to analyze');
    return null;
  }
  
  // Group by test name
  const testGroups: Record<string, any[]> = {};
  
  labResults.forEach(lab => {
    const testName = lab.test_name || 'unknown';
    if (!testGroups[testName]) {
      testGroups[testName] = [];
    }
    testGroups[testName].push(lab);
  });
  
  // Analyze each test group for trends
  const testAnalysis: Record<string, any> = {};
  
  Object.keys(testGroups).forEach(testName => {
    const tests = testGroups[testName];
    
    // Sort by date
    tests.sort((a, b) => {
      const dateA = a.date ? new Date(a.date).getTime() : 0;
      const dateB = b.date ? new Date(b.date).getTime() : 0;
      return dateA - dateB;
    });
    
    // Extract values if numeric
    const numericResults = tests
      .filter(test => !isNaN(parseFloat(test.result_value)))
      .map(test => ({
        date: test.date,
        value: parseFloat(test.result_value),
        unit: test.unit
      }));
      
    // Calculate min, max, average if we have numeric results
    let valueStats = null;
    if (numericResults.length > 0) {
      const values = numericResults.map(r => r.value);
      valueStats = {
        min: Math.min(...values),
        max: Math.max(...values),
        avg: values.reduce((sum, val) => sum + val, 0) / values.length,
        unit: numericResults[0].unit || '',
        count: numericResults.length,
        first_date: numericResults[0].date,
        last_date: numericResults[numericResults.length - 1].date,
        all_values: numericResults.map(r => ({ 
          date: r.date, 
          value: r.value 
        }))
      };
    }
    
    testAnalysis[testName] = {
      count: tests.length,
      first_test_date: tests[0].date,
      last_test_date: tests[tests.length - 1].date,
      value_stats: valueStats,
    };
  });
  
  const labAnalysis = {
    total_lab_tests: labResults.length,
    unique_test_types: Object.keys(testGroups).length,
    test_frequency: Object.keys(testGroups).map(test => ({
      name: test,
      count: testGroups[test].length
    })).sort((a, b) => b.count - a.count),
    test_details: testAnalysis
  };
  
  saveAnalysis('lab_results_analysis.json', labAnalysis);
  return labAnalysis;
}

// Analyze conditions
function analyzeConditions() {
  console.log('Analyzing conditions...');
  const conditions = getFilesFromDir('conditions');
  
  if (conditions.length === 0) {
    console.log('No conditions to analyze');
    return null;
  }
  
  // Group by status
  const statusGroups: Record<string, any[]> = {};
  conditions.forEach(condition => {
    const status = condition.status || 'unknown';
    if (!statusGroups[status]) {
      statusGroups[status] = [];
    }
    statusGroups[status].push(condition);
  });
  
  // Group by diagnosis date (year)
  const yearGroups: Record<string, any[]> = {};
  conditions.forEach(condition => {
    if (!condition.diagnosis_date) return;
    
    const year = new Date(condition.diagnosis_date).getFullYear().toString();
    if (!yearGroups[year]) {
      yearGroups[year] = [];
    }
    yearGroups[year].push(condition);
  });
  
  const conditionsAnalysis = {
    total_conditions: conditions.length,
    by_status: Object.keys(statusGroups).map(status => ({
      status,
      count: statusGroups[status].length,
      conditions: statusGroups[status].map(c => c.name)
    })),
    by_year: Object.keys(yearGroups).sort().map(year => ({
      year,
      count: yearGroups[year].length,
      conditions: yearGroups[year].map(c => c.name)
    }))
  };
  
  saveAnalysis('conditions_analysis.json', conditionsAnalysis);
  return conditionsAnalysis;
}

// Analyze medical events and appointments
function analyzeMedicalEvents() {
  console.log('Analyzing medical events...');
  const appointments = getFilesFromDir('appointments');
  
  if (appointments.length === 0) {
    console.log('No appointments to analyze');
    return null;
  }
  
  // Group by provider
  const providerGroups: Record<string, any[]> = {};
  appointments.forEach(appt => {
    const provider = appt.provider_name || 'unknown';
    if (!providerGroups[provider]) {
      providerGroups[provider] = [];
    }
    providerGroups[provider].push(appt);
  });
  
  // Group by year
  const yearGroups: Record<string, any[]> = {};
  appointments.forEach(appt => {
    if (!appt.date) return;
    
    const year = new Date(appt.date).getFullYear().toString();
    if (!yearGroups[year]) {
      yearGroups[year] = [];
    }
    yearGroups[year].push(appt);
  });
  
  // Analyze frequency by month
  const monthCounts: Record<string, number> = {};
  appointments.forEach(appt => {
    if (!appt.date) return;
    
    const date = new Date(appt.date);
    const monthYear = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    
    if (!monthCounts[monthYear]) {
      monthCounts[monthYear] = 0;
    }
    monthCounts[monthYear]++;
  });
  
  const eventsAnalysis = {
    total_appointments: appointments.length,
    by_provider: Object.keys(providerGroups).map(provider => ({
      provider,
      count: providerGroups[provider].length,
    })).sort((a, b) => b.count - a.count),
    by_year: Object.keys(yearGroups).sort().map(year => ({
      year,
      count: yearGroups[year].length,
    })),
    monthly_frequency: Object.keys(monthCounts).sort().map(month => ({
      month,
      count: monthCounts[month]
    }))
  };
  
  saveAnalysis('medical_events_analysis.json', eventsAnalysis);
  return eventsAnalysis;
}

// Analyze medications
function analyzeMedications() {
  console.log('Analyzing medications...');
  const medications = getFilesFromDir('medications');
  
  if (medications.length === 0) {
    console.log('No medications to analyze');
    return null;
  }
  
  // Group by active status
  const statusGroups: Record<string, any[]> = {};
  medications.forEach(med => {
    const status = med.active || 'unknown';
    if (!statusGroups[status]) {
      statusGroups[status] = [];
    }
    statusGroups[status].push(med);
  });
  
  // Group by condition being treated
  const conditionGroups: Record<string, any[]> = {};
  medications.forEach(med => {
    if (!med.condition || !med.condition.name) {
      if (!conditionGroups['unknown']) {
        conditionGroups['unknown'] = [];
      }
      conditionGroups['unknown'].push(med);
      return;
    }
    
    const condition = med.condition.name;
    if (!conditionGroups[condition]) {
      conditionGroups[condition] = [];
    }
    conditionGroups[condition].push(med);
  });
  
  const medsAnalysis = {
    total_medications: medications.length,
    by_status: Object.keys(statusGroups).map(status => ({
      status,
      count: statusGroups[status].length,
      medications: statusGroups[status].map(m => m.name)
    })),
    by_condition: Object.keys(conditionGroups).map(condition => ({
      condition,
      count: conditionGroups[condition].length,
      medications: conditionGroups[condition].map(m => m.name)
    }))
  };
  
  saveAnalysis('medications_analysis.json', medsAnalysis);
  return medsAnalysis;
}

// Generate text analysis from notes and imaging reports
function analyzeTextData() {
  console.log('Analyzing text data from notes and imaging...');
  const notes = getFilesFromDir('notes');
  const imaging = getFilesFromDir('imaging');
  
  const allTextData = [...notes, ...imaging];
  
  if (allTextData.length === 0) {
    console.log('No text data to analyze');
    return null;
  }
  
  // Simple keyword frequency analysis
  const keywordCounts: Record<string, number> = {};
  const commonMedicalKeywords = [
    'pain', 'chronic', 'acute', 'inflammation', 'normal', 'abnormal',
    'sprain', 'strain', 'fracture', 'tear', 'rupture', 'degeneration',
    'stenosis', 'arthritis', 'spondylosis', 'herniation', 'protrusion',
    'edema', 'effusion', 'surgery', 'trauma', 'injury'
  ];
  
  allTextData.forEach(item => {
    if (!item.content) return;
    
    const content = item.content.toLowerCase();
    
    commonMedicalKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
      const matches = content.match(regex);
      
      if (matches) {
        if (!keywordCounts[keyword]) {
          keywordCounts[keyword] = 0;
        }
        keywordCounts[keyword] += matches.length;
      }
    });
  });
  
  // Group by source
  const sourceGroups: Record<string, any[]> = {};
  allTextData.forEach(item => {
    const source = item.source || 'unknown';
    if (!sourceGroups[source]) {
      sourceGroups[source] = [];
    }
    sourceGroups[source].push(item);
  });
  
  const textAnalysis = {
    total_text_documents: allTextData.length,
    notes_count: notes.length,
    imaging_count: imaging.length,
    keyword_frequency: Object.keys(keywordCounts)
      .map(keyword => ({ keyword, count: keywordCounts[keyword] }))
      .sort((a, b) => b.count - a.count),
    by_source: Object.keys(sourceGroups).map(source => ({
      source,
      count: sourceGroups[source].length
    }))
  };
  
  saveAnalysis('text_content_analysis.json', textAnalysis);
  return textAnalysis;
}

// Generate complete timeline
function generateTimeline() {
  console.log('Generating comprehensive health timeline...');
  
  // Get all data with dates
  const appointments = getFilesFromDir('appointments')
    .filter(a => a.date)
    .map(a => ({
      type: 'appointment',
      date: a.date,
      title: a.title || 'Unknown appointment',
      provider: a.provider_name,
      details: a
    }));
    
  const labResults = getFilesFromDir('lab_results')
    .filter(l => l.date)
    .map(l => ({
      type: 'lab_result',
      date: l.date,
      title: `${l.test_name || 'Lab test'}: ${l.result_value || 'No value'} ${l.unit || ''}`,
      details: l
    }));
    
  const conditions = getFilesFromDir('conditions')
    .filter(c => c.diagnosis_date)
    .map(c => ({
      type: 'condition',
      date: c.diagnosis_date,
      title: `Diagnosed: ${c.name || 'Unknown condition'}`,
      status: c.status,
      details: c
    }));
    
  const medications = getFilesFromDir('medications')
    .filter(m => m.start_date)
    .map(m => ({
      type: 'medication',
      date: m.start_date,
      title: `Started: ${m.name || 'Unknown medication'}`,
      details: m
    }));
    
  const imaging = getFilesFromDir('imaging')
    .filter(i => i.date)
    .map(i => ({
      type: 'imaging',
      date: i.date,
      title: i.name || 'Imaging study',
      details: i
    }));
    
  // Combine all events
  const allEvents = [
    ...appointments,
    ...labResults,
    ...conditions,
    ...medications,
    ...imaging
  ];
  
  // Sort by date
  allEvents.sort((a, b) => {
    const dateA = new Date(a.date).getTime();
    const dateB = new Date(b.date).getTime();
    return dateA - dateB;
  });
  
  // Group by year and month
  const eventsByMonth: Record<string, any[]> = {};
  
  allEvents.forEach(event => {
    const date = new Date(event.date);
    const yearMonth = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    
    if (!eventsByMonth[yearMonth]) {
      eventsByMonth[yearMonth] = [];
    }
    
    eventsByMonth[yearMonth].push(event);
  });
  
  const timeline = {
    total_events: allEvents.length,
    events_by_type: {
      appointments: appointments.length,
      lab_results: labResults.length,
      conditions: conditions.length,
      medications: medications.length,
      imaging: imaging.length
    },
    first_event: allEvents.length > 0 ? allEvents[0] : null,
    last_event: allEvents.length > 0 ? allEvents[allEvents.length - 1] : null,
    all_events: allEvents,
    events_by_month: Object.keys(eventsByMonth).sort().map(month => ({
      month,
      events: eventsByMonth[month]
    }))
  };
  
  saveAnalysis('comprehensive_timeline.json', timeline);
  return timeline;
}

// Generate data completeness report
function generateCompletenessReport() {
  console.log('Generating data completeness report...');
  
  // Count data in each category
  const counts = {
    lab_results: countFilesInDir('lab_results'),
    appointments: countFilesInDir('appointments'),
    conditions: countFilesInDir('conditions'),
    providers: countFilesInDir('providers'),
    medications: countFilesInDir('medications'),
    symptoms: countFilesInDir('symptoms'),
    imaging: countFilesInDir('imaging'),
    notes: countFilesInDir('notes')
  };
  
  // Check date ranges for each category to identify potential gaps
  
  // Lab results date range
  const labResults = getFilesFromDir('lab_results')
    .filter(l => l.date)
    .map(l => new Date(l.date).getTime());
  
  const labDateRange = labResults.length > 0 ? {
    first_date: new Date(Math.min(...labResults)).toISOString().split('T')[0],
    last_date: new Date(Math.max(...labResults)).toISOString().split('T')[0],
    count: labResults.length
  } : null;
  
  // Appointments date range
  const apptDates = getFilesFromDir('appointments')
    .filter(a => a.date)
    .map(a => new Date(a.date).getTime());
  
  const apptDateRange = apptDates.length > 0 ? {
    first_date: new Date(Math.min(...apptDates)).toISOString().split('T')[0],
    last_date: new Date(Math.max(...apptDates)).toISOString().split('T')[0],
    count: apptDates.length
  } : null;
  
  // Generate a report on what data appears to be missing
  const potentialGaps = [];
  
  // Check for common lab tests that are typically done regularly
  const labTestNames = getFilesFromDir('lab_results')
    .map(l => l.test_name)
    .filter(Boolean);
  
  const uniqueLabTests = [...new Set(labTestNames)];
  
  const commonLabTests = [
    'Complete Blood Count',
    'Comprehensive Metabolic Panel',
    'Lipid Panel',
    'Hemoglobin A1C',
    'Vitamin D',
    'Thyroid Stimulating Hormone'
  ];
  
  commonLabTests.forEach(test => {
    const hasTest = uniqueLabTests.some(t => 
      t.toLowerCase().includes(test.toLowerCase())
    );
    
    if (!hasTest) {
      potentialGaps.push(`Common lab test "${test}" not found in data`);
    }
  });
  
  // Check for primary care visits
  const appointments = getFilesFromDir('appointments');
  const hasPrimaryCare = appointments.some(a => 
    (a.provider_specialty && a.provider_specialty.toLowerCase().includes('primary')) ||
    (a.department && a.department.toLowerCase().includes('family medicine')) ||
    (a.title && a.title.toLowerCase().includes('primary care'))
  );
  
  if (!hasPrimaryCare) {
    potentialGaps.push('No clear primary care/annual physical visits found');
  }
  
  // Generate final report
  const completenessReport = {
    data_counts: counts,
    total_records: Object.values(counts).reduce((sum, count) => sum + count, 0),
    date_ranges: {
      lab_results: labDateRange,
      appointments: apptDateRange
    },
    potential_data_gaps: potentialGaps,
    data_sources: fs.existsSync(path.join(DATA_DIR, 'data_summary.json')) 
      ? loadJson('data_summary.json').data_sources
      : ['unknown']
  };
  
  saveAnalysis('data_completeness_report.json', completenessReport);
  return completenessReport;
}

// Run all analysis functions
async function runAnalysis() {
  console.log('Starting health data analysis...');
  
  if (!fs.existsSync(DATA_DIR)) {
    console.error(`Data directory ${DATA_DIR} does not exist. Run export-all-to-json.ts first.`);
    process.exit(1);
  }
  
  const labAnalysis = analyzeLabResults();
  const conditionsAnalysis = analyzeConditions();
  const eventsAnalysis = analyzeMedicalEvents();
  const medsAnalysis = analyzeMedications();
  const textAnalysis = analyzeTextData();
  const timeline = generateTimeline();
  const completenessReport = generateCompletenessReport();
  
  // Generate summary report with key insights
  const insightsSummary = {
    analysis_date: new Date().toISOString(),
    total_records_analyzed: Object.keys(completenessReport.data_counts)
      .reduce((sum, key) => sum + completenessReport.data_counts[key], 0),
    key_stats: {
      conditions: conditionsAnalysis?.total_conditions || 0,
      active_medications: medsAnalysis?.by_status?.find(s => s.status === 'active')?.count || 0,
      lab_tests: labAnalysis?.total_lab_tests || 0,
      appointments: eventsAnalysis?.total_appointments || 0
    },
    time_span: timeline?.all_events?.length > 0 ? {
      first_record_date: timeline.first_event.date,
      last_record_date: timeline.last_event.date,
      total_days: timeline.all_events.length > 0 ? 
        Math.round((new Date(timeline.last_event.date).getTime() - 
                    new Date(timeline.first_event.date).getTime()) / (1000 * 60 * 60 * 24)) : 0
    } : null,
    most_frequent_lab_tests: labAnalysis?.test_frequency?.slice(0, 5) || [],
    most_common_medical_terms: textAnalysis?.keyword_frequency?.slice(0, 10) || [],
    data_completeness: {
      potential_gaps: completenessReport.potential_data_gaps,
      missing_data_categories: Object.entries(completenessReport.data_counts)
        .filter(([_, count]) => count === 0)
        .map(([category]) => category)
    }
  };
  
  saveAnalysis('health_data_insights.json', insightsSummary);
  
  // Generate Markdown summary for easy reading
  const markdownSummary = `# Health Data Analysis Summary
  
## Overview
- **Analysis Date:** ${new Date().toLocaleString()}
- **Total Records Analyzed:** ${insightsSummary.total_records_analyzed}
- **Time Span:** ${insightsSummary.time_span ? 
    `${insightsSummary.time_span.first_record_date} to ${insightsSummary.time_span.last_record_date} (${insightsSummary.time_span.total_days} days)` : 
    'Unknown'}

## Key Statistics
- **Medical Conditions:** ${insightsSummary.key_stats.conditions}
- **Active Medications:** ${insightsSummary.key_stats.active_medications}
- **Lab Tests:** ${insightsSummary.key_stats.lab_tests}
- **Appointments/Visits:** ${insightsSummary.key_stats.appointments}

## Most Frequent Lab Tests
${insightsSummary.most_frequent_lab_tests.map(test => `- ${test.name}: ${test.count} times`).join('\n')}

## Most Common Medical Terms in Notes
${insightsSummary.most_common_medical_terms.map(term => `- "${term.keyword}": ${term.count} mentions`).join('\n')}

## Data Completeness
${insightsSummary.data_completeness.missing_data_categories.length > 0 ? 
  `### Missing Data Categories\n${insightsSummary.data_completeness.missing_data_categories.map(category => `- ${category}`).join('\n')}` : 
  '- All major data categories have some data'}

${insightsSummary.data_completeness.potential_gaps.length > 0 ? 
  `### Potential Data Gaps\n${insightsSummary.data_completeness.potential_gaps.map(gap => `- ${gap}`).join('\n')}` : 
  '- No obvious data gaps detected'}

## Data Distribution
- **Lab Results:** ${completenessReport.data_counts.lab_results}
- **Appointments:** ${completenessReport.data_counts.appointments}
- **Conditions:** ${completenessReport.data_counts.conditions}
- **Medications:** ${completenessReport.data_counts.medications}
- **Imaging Studies:** ${completenessReport.data_counts.imaging}
- **Clinical Notes:** ${completenessReport.data_counts.notes}
- **Providers:** ${completenessReport.data_counts.providers}
- **Symptoms:** ${completenessReport.data_counts.symptoms}

---
*Data sources: ${completenessReport.data_sources.join(', ')}*
*For detailed analysis, see the JSON files in the data/analysis directory.*
`;
  
  fs.writeFileSync(path.join(OUTPUT_DIR, 'health_data_summary.md'), markdownSummary);
  console.log(`Saved Markdown summary to ${path.join(OUTPUT_DIR, 'health_data_summary.md')}`);
  
  console.log('-----------------------------------');
  console.log('Analysis complete!');
  console.log(`All analysis results saved to: ${OUTPUT_DIR}`);
  console.log('-----------------------------------');
}

// Run the analysis
runAnalysis().catch(err => {
  console.error('Error during analysis:', err);
  process.exit(1);
}); 