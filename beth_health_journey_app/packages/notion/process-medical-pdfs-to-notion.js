const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { Configuration, OpenAIApi } = require('openai');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

// Constants
const PDF_BASE_DIR = path.join(process.cwd(), 'data/atrium-exports/all_import');
const OUTPUT_DIR = path.join(process.cwd(), 'data/processed');

// Notion database IDs
const NOTION_MEDICAL_CALENDAR_DB = '17b86edc-ae2c-81c1-83e0-e0a19a035932';
const NOTION_MEDICAL_TEAM_DB = '17b86edc-ae2c-8155-8caa-fbb80647f6a9';
const NOTION_CONDITIONS_DB = '17b86edc-ae2c-8167-ba15-f9f03b49795e';

// Configure OpenAI
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// Configure Supabase
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Helper: Ensure directory exists
function ensureDirectoryExists(directoryPath) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
}

// Helper: Extract text from PDF
async function extractTextFromPdf(pdfPath) {
  try {
    // First try pdftotext if available
    try {
      return execSync(`pdftotext "${pdfPath}" -`, { encoding: 'utf-8' });
    } catch (e) {
      console.log(`Note: pdftotext not available for ${path.basename(pdfPath)}`);
      
      // Try using textutil as a fallback on macOS
      try {
        const tempFile = path.join(process.cwd(), 'temp_pdf_text.txt');
        execSync(`textutil -convert txt -stdout "${pdfPath}" > "${tempFile}"`, { encoding: 'utf-8' });
        const content = fs.readFileSync(tempFile, 'utf-8');
        fs.unlinkSync(tempFile);
        return content;
      } catch (e2) {
        console.log(`Unable to extract text from PDF: ${e2.message}`);
        return '';
      }
    }
  } catch (error) {
    console.error(`Error extracting text from ${pdfPath}: ${error.message}`);
    return '';
  }
}

// Helper: Extract path info
function extractPathInfo(filePath) {
  // Pattern: data/atrium-exports/all_import/2023/Endocrinology/06_June 15 2023 - Dr Gagneet/TSH.pdf
  const parts = filePath.split(path.sep);
  const year = parts[3];
  const specialty = parts[4];
  
  // Extract date and doctor from folder name
  const visitFolder = parts[5];
  const fileName = path.basename(filePath, path.extname(filePath));
  
  // Parse the folder name which often has format: MM_Month DD YYYY - Dr Name
  let visitDate = null;
  let doctorName = null;
  
  // Try to extract date with regex
  const dateMatch = visitFolder.match(/(\d+)_([A-Za-z]+)\s+(\d+)\s+(\d{4})/);
  if (dateMatch) {
    const month = dateMatch[2];
    const day = dateMatch[3];
    const year = dateMatch[4];
    visitDate = `${month} ${day}, ${year}`;
  }
  
  // Try to extract doctor name
  const doctorMatch = visitFolder.match(/Dr\.?\s+([A-Za-z]+)/i) || visitFolder.match(/\-\s+([^\/]+)$/);
  if (doctorMatch) {
    doctorName = doctorMatch[1].trim();
  }
  
  return {
    year,
    specialty,
    visitDate,
    doctorName,
    testName: fileName
  };
}

// Lookup or create provider in Supabase
async function lookupOrCreateProvider(providerName, specialty) {
  if (!providerName) return null;
  
  // Try to find provider by name
  const { data: existingProviders } = await supabase
    .from('providers')
    .select('*')
    .ilike('name', `%${providerName}%`)
    .limit(1);
    
  if (existingProviders && existingProviders.length > 0) {
    console.log(`Found existing provider: ${existingProviders[0].name}`);
    return existingProviders[0].id;
  }
  
  // Create new provider if not found
  const { data: newProvider, error } = await supabase
    .from('providers')
    .insert({
      name: providerName,
      specialty: specialty || '',
      facility: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    .select();
    
  if (error) {
    console.error(`Error creating provider: ${error.message}`);
    return null;
  }
  
  console.log(`Created new provider: ${providerName}`);
  return newProvider[0].id;
}

// Enhanced analysis with deeper medical context
async function analyzePdfContent(text, fileInfo) {
  try {
    const prompt = `
You are a medical data extraction assistant with expert knowledge in clinical documentation. Please analyze the following medical document text and provide structured information.

Document details:
- Year: ${fileInfo.year}
- Specialty: ${fileInfo.specialty}
- Visit Date: ${fileInfo.visitDate}
- Doctor: ${fileInfo.doctorName}
- File Name: ${fileInfo.testName}

Text content:
${text.substring(0, 6000)} 

Please provide the following information in JSON format:
{
  "documentType": "lab_result" or "appointment_notes" or "medical_image" or "other",
  "testName": "", // If lab result, the name of the test (e.g., "Comprehensive Metabolic Panel", "TSH")
  "testDate": "", // The date when the test was performed in ISO format (YYYY-MM-DD)
  "testResult": "", // The actual result value (e.g., "5.2")
  "unit": "", // Unit of measurement (e.g., "mg/dL", "mIU/L")
  "referenceRange": "", // Normal range (e.g., "0.4-4.0")
  "isAbnormal": true/false, // Whether the result is outside normal range
  "visitPurpose": "", // For appointment notes: reason for visit
  "doctorName": "", // The doctor who conducted the test/appointment
  "notes": "", // Important clinical findings, recommendations, or next steps
  "summaryForPatient": "", // A simplified 2-3 sentence explanation of key takeaways in plain English
  "relevantConditions": [], // Related medical conditions mentioned
  "followUpNeeded": true/false, // Whether follow-up is recommended
  "medications": [], // Any medications mentioned
  "category": "", // Category like "Blood Work", "Imaging", "Thyroid", etc.
  "medicalSpecialty": "" // Medical specialty this relates to
}

For lab results, extract exact values, units, and reference ranges. For appointment notes, focus on diagnosis, treatment plans, and follow-up instructions. If multiple test results are in a single document, focus on the most important one and mention others in notes.
`;

    const response = await openai.createChatCompletion({
      model: "gpt-4",
      messages: [
        { role: "system", content: "You are a specialized medical data extraction assistant with clinical expertise." },
        { role: "user", content: prompt }
      ],
      temperature: 0.1,
      max_tokens: 1500
    });

    try {
      const responseText = response.data.choices[0].message.content;
      return JSON.parse(responseText);
    } catch (e) {
      console.error("Error parsing JSON from OpenAI response:", e);
      return null;
    }
  } catch (error) {
    console.error("Error calling OpenAI:", error);
    return null;
  }
}

// Check if record exists in Notion using MCP Notion integration
async function checkIfRecordExistsInNotion(testName, testDate, type) {
  if (!testName || !testDate) return false;
  
  try {
    // Format date for Notion query
    let formattedDate = testDate;
    if (testDate && !testDate.includes('T')) {
      // Convert to ISO format if not already
      formattedDate = new Date(testDate).toISOString().split('T')[0];
    }
    
    // Query Notion database
    const response = await global.mcp_notion_notion_query_database({
      database_id: NOTION_MEDICAL_CALENDAR_DB,
      filter: {
        and: [
          {
            property: "Name",
            title: {
              contains: testName
            }
          },
          {
            property: "Date",
            date: {
              equals: formattedDate
            }
          }
        ]
      },
      page_size: 1
    });
    
    // Parse response
    const result = JSON.parse(response);
    return result.results && result.results.length > 0;
  } catch (error) {
    console.error(`Error checking Notion: ${error.message}`);
    return false;
  }
}

// Add to Supabase based on document type
async function addToSupabase(data, fileInfo) {
  try {
    // Look up or create provider
    const providerId = await lookupOrCreateProvider(
      data.doctorName || fileInfo.doctorName, 
      data.medicalSpecialty || fileInfo.specialty
    );
    
    // Add to appropriate table based on document type
    if (data.documentType === "lab_result") {
      // Format data for lab_results table
      const { data: labResult, error } = await supabase
        .from('lab_results')
        .insert({
          test_name: data.testName,
          category: data.category,
          date: data.testDate || fileInfo.visitDate,
          result: data.testResult,
          unit: data.unit,
          reference_range: data.referenceRange,
          is_abnormal: data.isAbnormal,
          provider_id: providerId,
          notes: data.notes,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select();
        
      if (error) {
        console.error(`Error adding lab result to Supabase: ${error.message}`);
        return null;
      }
      
      console.log(`Added lab result to Supabase: ${labResult[0].id}`);
      return labResult[0].id;
    } 
    else if (data.documentType === "appointment_notes") {
      // Create a medical event for appointment notes
      const { data: medicalEvent, error } = await supabase
        .from('medical_events')
        .insert({
          title: data.visitPurpose || `Visit with ${data.doctorName || fileInfo.doctorName}`,
          description: data.notes,
          event_type: 'appointment',
          date: data.testDate || fileInfo.visitDate,
          location: fileInfo.specialty ? `${fileInfo.specialty} Office` : '',
          provider_id: providerId,
          notes: data.summaryForPatient || data.notes,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select();
        
      if (error) {
        console.error(`Error adding medical event to Supabase: ${error.message}`);
        return null;
      }
      
      console.log(`Added medical event to Supabase: ${medicalEvent[0].id}`);
      return medicalEvent[0].id;
    }
    else {
      console.log(`Unsupported document type for Supabase: ${data.documentType}`);
      return null;
    }
  } catch (error) {
    console.error(`Error adding to Supabase: ${error.message}`);
    return null;
  }
}

// Add medical calendar entry to Notion using MCP Notion integration
async function addMedicalCalendarEntryToNotion(data, fileInfo) {
  try {
    // Format date for Notion
    let formattedDate = data.testDate || fileInfo.visitDate;
    if (formattedDate) {
      // Try to parse and format as ISO
      try {
        formattedDate = new Date(formattedDate).toISOString();
      } catch (e) {
        console.log(`Could not parse date: ${formattedDate}`);
      }
    }
    
    // Construct properties for Notion database item
    const properties = {
      "Name": {
        "title": [
          {
            "text": {
              "content": data.testName || data.visitPurpose || fileInfo.testName || "Medical Record"
            }
          }
        ]
      },
      "Date": {
        "date": {
          "start": formattedDate || new Date().toISOString()
        }
      },
      "Type": {
        "select": {
          "name": data.documentType === "lab_result" ? "Lab Result" : 
                 data.documentType === "appointment_notes" ? "Doctor Notes" :
                 data.documentType === "medical_image" ? "Image/Scan" : "Record"
        }
      }
    };
    
    // Add lab result details
    if (data.documentType === "lab_result") {
      if (data.testResult) {
        properties["Lab Result"] = {
          "rich_text": [
            {
              "text": {
                "content": data.testResult
              }
            }
          ]
        };
      }
      
      if (data.unit) {
        properties["Unit"] = {
          "rich_text": [
            {
              "text": {
                "content": data.unit
              }
            }
          ]
        };
      }
      
      if (data.referenceRange) {
        properties["Reference Range"] = {
          "rich_text": [
            {
              "text": {
                "content": data.referenceRange
              }
            }
          ]
        };
      }
      
      if (data.category) {
        properties["Category"] = {
          "select": {
            "name": data.category
          }
        };
      }
      
      if (data.isAbnormal !== undefined) {
        properties["Abnormal"] = {
          "checkbox": data.isAbnormal
        };
      }
    }
    
    // Add appointment details
    if (data.documentType === "appointment_notes") {
      if (data.summaryForPatient) {
        properties["Summary"] = {
          "rich_text": [
            {
              "text": {
                "content": data.summaryForPatient
              }
            }
          ]
        };
      }
      
      if (data.notes) {
        properties["Visit Summary"] = {
          "rich_text": [
            {
              "text": {
                "content": data.notes
              }
            }
          ]
        };
      }
      
      if (data.doctorName || fileInfo.doctorName) {
        properties["Doctor"] = {
          "rich_text": [
            {
              "text": {
                "content": data.doctorName || fileInfo.doctorName
              }
            }
          ]
        };
      }
      
      if (data.medicalSpecialty || fileInfo.specialty) {
        properties["Specialty"] = {
          "select": {
            "name": data.medicalSpecialty || fileInfo.specialty
          }
        };
      }
      
      if (data.followUpNeeded !== undefined) {
        properties["Follow-up Needed"] = {
          "checkbox": data.followUpNeeded
        };
      }
    }
    
    // Create the item in Notion
    const response = await global.mcp_notion_notion_create_database_item({
      database_id: NOTION_MEDICAL_CALENDAR_DB,
      properties: properties
    });
    
    // Parse response and get page ID
    const result = JSON.parse(response);
    console.log(`Added to Notion Medical Calendar: ${result.id}`);
    
    // If there are relevant conditions, link them
    if (data.relevantConditions && data.relevantConditions.length > 0) {
      await addConditionsToNotion(data.relevantConditions, result.id);
    }
    
    return result.id;
  } catch (error) {
    console.error(`Error adding to Notion: ${error.message}`);
    return null;
  }
}

// Add conditions to Notion
async function addConditionsToNotion(conditions, relatedPageId) {
  for (const condition of conditions) {
    try {
      // Check if condition exists
      const response = await global.mcp_notion_notion_query_database({
        database_id: NOTION_CONDITIONS_DB,
        filter: {
          property: "Name",
          title: {
            contains: condition
          }
        },
        page_size: 1
      });
      
      const result = JSON.parse(response);
      
      if (result.results && result.results.length > 0) {
        console.log(`Found existing condition: ${condition}`);
        // Link to the medical calendar entry
        // This would require adding a relation property in your Notion database
      } else {
        console.log(`Creating new condition: ${condition}`);
        // Create new condition
        await global.mcp_notion_notion_create_database_item({
          database_id: NOTION_CONDITIONS_DB,
          properties: {
            "Name": {
              "title": [
                {
                  "text": {
                    "content": condition
                  }
                }
              ]
            },
            "Status": {
              "select": {
                "name": "active"
              }
            },
            "Date Diagnosed": {
              "date": {
                "start": new Date().toISOString()
              }
            }
          }
        });
      }
    } catch (error) {
      console.error(`Error handling condition "${condition}": ${error.message}`);
    }
  }
}

// Process a single PDF file
async function processPdfFile(filePath) {
  console.log(`Processing: ${filePath}`);
  
  // Extract text from PDF
  const text = await extractTextFromPdf(filePath);
  if (!text || text.trim() === '') {
    console.log(`No text extracted from ${filePath}`);
    return;
  }
  
  // Extract information from the file path
  const fileInfo = extractPathInfo(filePath);
  
  // Analyze the content
  const analysis = await analyzePdfContent(text, fileInfo);
  if (!analysis) {
    console.log(`Analysis failed for ${filePath}`);
    return;
  }
  
  // Save the processed data
  const outputPath = path.join(OUTPUT_DIR, path.relative(PDF_BASE_DIR, filePath) + '.json');
  ensureDirectoryExists(path.dirname(outputPath));
  fs.writeFileSync(outputPath, JSON.stringify(analysis, null, 2));
  
  // Check if it already exists in Notion
  const exists = await checkIfRecordExistsInNotion(
    analysis.testName || fileInfo.testName, 
    analysis.testDate || fileInfo.visitDate,
    analysis.documentType
  );
  
  if (!exists) {
    // Add to Notion
    const notionPageId = await addMedicalCalendarEntryToNotion(analysis, fileInfo);
    console.log(`Added to Notion: ${notionPageId}`);
    
    // Add to Supabase
    const supabaseId = await addToSupabase(analysis, fileInfo);
    console.log(`Added to Supabase: ${supabaseId}`);
  } else {
    console.log(`Record already exists in Notion, skipping.`);
  }
}

// Process all PDFs in a directory
async function processDirectory(dirPath) {
  const files = fs.readdirSync(dirPath, { withFileTypes: true });
  
  for (const file of files) {
    const fullPath = path.join(dirPath, file.name);
    
    if (file.isDirectory()) {
      await processDirectory(fullPath);
    } else if (file.name.toLowerCase().endsWith('.pdf')) {
      await processPdfFile(fullPath);
    }
  }
}

// Main function
async function main() {
  console.log("Starting medical PDF processing pipeline...");
  ensureDirectoryExists(OUTPUT_DIR);
  
  // Validate environment
  if (!process.env.OPENAI_API_KEY) {
    console.error("OPENAI_API_KEY not found in environment variables");
    process.exit(1);
  }
  
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    console.error("Supabase credentials not found in environment variables");
    process.exit(1);
  }
  
  // Check if MCP Notion functions are available
  if (!global.mcp_notion_notion_query_database || !global.mcp_notion_notion_create_database_item) {
    console.error("MCP Notion functions not available. Make sure you're running this in the correct environment.");
    process.exit(1);
  }
  
  // Get command line args
  const args = process.argv.slice(2);
  const startYear = args[0] || '2018';
  const endYear = args[1] || '2025';
  
  console.log(`Processing PDFs from years ${startYear} to ${endYear}`);
  
  // Process specific year ranges
  for (let year = parseInt(startYear); year <= parseInt(endYear); year++) {
    const yearDir = path.join(PDF_BASE_DIR, year.toString());
    if (fs.existsSync(yearDir)) {
      console.log(`Processing year: ${year}`);
      await processDirectory(yearDir);
    } else {
      console.log(`Directory for year ${year} not found, skipping.`);
    }
  }
  
  console.log('Processing complete!');
}

// Check if MCP functions are available as globals
if (typeof global.mcp_notion_notion_query_database === 'undefined') {
  // If running outside MCP environment, create mock functions for testing
  global.mcp_notion_notion_query_database = async function(params) {
    console.log(`MOCK: Querying Notion database ${params.database_id}`);
    return JSON.stringify({ results: [] });
  };
  
  global.mcp_notion_notion_create_database_item = async function(params) {
    console.log(`MOCK: Creating item in Notion database ${params.database_id}`);
    return JSON.stringify({ id: 'mock-page-id-' + Date.now() });
  };
}

main().catch(console.error); 