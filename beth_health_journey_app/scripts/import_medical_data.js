// Import Medical Data to Notion
// This script helps import medical data from extracted text files into Notion databases

require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { Client } = require('@notionhq/client');
const { parseLabResult, formatLabSummary } = require('./lab_result_parser');

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_API_KEY,
});

// Database IDs
const DATABASES = {
  MEDICAL_CALENDAR: '17b86edcae2c81c183e0e0a19a035932',
  SYMPTOMS: '18a86edcae2c805a9ea1000c82df6d90',
  MEDICAL_TEAM: '17b86edcae2c81558caafbb80647f6a9',
  MEDICATIONS: '17b86edcae2c81a7b28ae9fbcc7e7b62',
  DIAGNOSES: '17b86edcae2c8167ba15f9f03b49795e',
  NOTES: '654e1ddc962f44698b1df6697375a321'
};

// Function to read all extracted text files
async function readExtractedFiles(directory) {
  const files = fs.readdirSync(directory);
  
  const fileContents = {};
  for (const file of files) {
    const filePath = path.join(directory, file);
    if (fs.statSync(filePath).isFile()) {
      const content = fs.readFileSync(filePath, 'utf8');
      fileContents[file] = content;
    }
  }
  
  return fileContents;
}

// Function to parse date from filename (format: MM_DD_YYYY)
function parseDateFromFilename(filename) {
  const dateMatch = filename.match(/(\d{2})_(\d{2})_(\d{4})/);
  if (dateMatch) {
    const [_, month, day, year] = dateMatch;
    return new Date(`${year}-${month}-${day}`);
  }
  return null;
}

// Function to parse doctor name from filename
function parseDoctorFromFilename(filename) {
  const doctorMatch = filename.match(/Dr([A-Za-z]+)/);
  if (doctorMatch) {
    return doctorMatch[1];
  }
  return null;
}

// Function to extract test type from filename
function extractTestType(filename) {
  const testTypes = {
    TSH: 'Thyroid Function',
    THYROID: 'Thyroid Function',
    METABOLIC: 'Metabolic Panel',
    LIPID: 'Lipid Panel',
    CBC: 'Complete Blood Count',
    HEMOGLOBIN: 'Hemoglobin',
    VITAMIN: 'Vitamin Levels',
    IRON: 'Iron Studies',
    RHEUMATOID: 'Rheumatology Panel',
    ANTIBODY: 'Antibody Test',
    COVID: 'COVID-19 Test',
    URINE: 'Urinalysis',
    LIVER: 'Liver Function',
    KIDNEY: 'Kidney Function',
    GLUCOSE: 'Glucose Test',
    MRI: 'MRI Scan',
    XRAY: 'X-Ray',
    CT: 'CT Scan',
    ULTRASOUND: 'Ultrasound'
  };
  
  for (const [key, value] of Object.entries(testTypes)) {
    if (filename.toUpperCase().includes(key)) {
      return value;
    }
  }
  
  return 'Lab Test';
}

// Function to check if a lab result already exists in Notion
async function checkLabResultExists(title, date) {
  try {
    const dateString = date.toISOString().split('T')[0];
    
    const response = await notion.databases.query({
      database_id: DATABASES.MEDICAL_CALENDAR,
      filter: {
        and: [
          {
            property: "Name",
            title: {
              contains: title.split(' - ')[0] // Just check for the test name part
            }
          },
          {
            property: "Date",
            date: {
              equals: dateString
            }
          },
          {
            property: "Type",
            select: {
              equals: "Lab Result"
            }
          }
        ]
      }
    });
    
    return response.results.length > 0;
  } catch (error) {
    console.error(`Error checking if lab result exists: ${title}`, error);
    return false;
  }
}

// Function to add a new lab result to the Medical Calendar database
async function addLabResultToNotion(labInfo) {
  try {
    // First check if this lab result already exists
    const exists = await checkLabResultExists(labInfo.title, labInfo.date);
    if (exists) {
      console.log(`Lab result already exists: ${labInfo.title}`);
      return null;
    }
    
    // Format the lab result content using our parser
    let formattedContent = labInfo.content;
    
    if (labInfo.parsedData) {
      formattedContent = formatLabSummary(labInfo.parsedData);
    }
    
    // Convert markdown content to Notion blocks
    const blocks = convertMarkdownToBlocks(formattedContent);
    
    // Create the page in Notion
    const response = await notion.pages.create({
      parent: {
        database_id: DATABASES.MEDICAL_CALENDAR,
      },
      properties: {
        Name: {
          title: [
            {
              text: {
                content: labInfo.title,
              },
            },
          ],
        },
        Date: {
          date: {
            start: labInfo.date.toISOString().split('T')[0],
          },
        },
        Type: {
          select: {
            name: "Lab Result",
          },
        },
        Doctor: labInfo.doctorId ? {
          relation: [
            {
              id: labInfo.doctorId,
            },
          ],
        } : undefined,
        Related_Diagnoses: labInfo.diagnosisIds && labInfo.diagnosisIds.length > 0 ? {
          relation: labInfo.diagnosisIds.map(id => ({ id })),
        } : undefined,
      },
      children: blocks,
    });
    
    console.log(`Added lab result: ${labInfo.title}`);
    return response;
  } catch (error) {
    console.error(`Error adding lab result: ${labInfo.title}`, error);
    return null;
  }
}

// Function to convert markdown to Notion blocks
function convertMarkdownToBlocks(markdown) {
  const blocks = [];
  const lines = markdown.split('\n');
  let i = 0;
  
  while (i < lines.length) {
    const line = lines[i].trim();
    
    if (line.startsWith('# ')) {
      // Heading 1
      blocks.push({
        object: "block",
        type: "heading_1",
        heading_1: {
          rich_text: [{
            type: "text",
            text: { content: line.substring(2) }
          }]
        }
      });
    } else if (line.startsWith('## ')) {
      // Heading 2
      blocks.push({
        object: "block",
        type: "heading_2",
        heading_2: {
          rich_text: [{
            type: "text",
            text: { content: line.substring(3) }
          }]
        }
      });
    } else if (line.startsWith('### ')) {
      // Heading 3
      blocks.push({
        object: "block",
        type: "heading_3",
        heading_3: {
          rich_text: [{
            type: "text",
            text: { content: line.substring(4) }
          }]
        }
      });
    } else if (line.startsWith('- ')) {
      // Bulleted list
      blocks.push({
        object: "block",
        type: "bulleted_list_item",
        bulleted_list_item: {
          rich_text: [{
            type: "text",
            text: { content: line.substring(2) }
          }]
        }
      });
    } else if (line.startsWith('|')) {
      // Table
      // Parse table rows until we reach a non-table line
      const tableRows = [];
      let headerRow = line;
      let dividerRow = lines[i + 1];
      
      if (dividerRow && dividerRow.trim().startsWith('|') && dividerRow.includes('-')) {
        // This is indeed a table with a header divider
        i += 2; // Skip header and divider rows
        
        // Parse header
        const headers = headerRow
          .split('|')
          .slice(1, -1) // Remove empty first/last elements
          .map(h => h.trim());
        
        // Collect rows
        while (i < lines.length && lines[i].trim().startsWith('|')) {
          const rowData = lines[i]
            .split('|')
            .slice(1, -1) // Remove empty first/last elements
            .map(cell => cell.trim());
          
          tableRows.push(rowData);
          i++;
        }
        
        // Create a paragraph block with formatted table content
        // (Notion API doesn't directly support tables yet)
        for (const row of tableRows) {
          let rowText = "";
          
          // Format each cell
          for (let j = 0; j < row.length; j++) {
            if (j < headers.length) {
              rowText += `**${headers[j]}:** ${row[j]}  `;
            } else {
              rowText += `${row[j]}  `;
            }
          }
          
          blocks.push({
            object: "block",
            type: "paragraph",
            paragraph: {
              rich_text: [{
                type: "text",
                text: { content: rowText }
              }]
            }
          });
        }
        
        continue; // Skip the i++ at the end since we've already advanced
      } else {
        // Not a proper table, treat as paragraph
        blocks.push({
          object: "block",
          type: "paragraph",
          paragraph: {
            rich_text: [{
              type: "text",
              text: { content: line }
            }]
          }
        });
      }
    } else if (line.length > 0) {
      // Check for bold/italic formatting
      let content = line;
      const formattedTexts = [];
      
      // Handle bold text (**text**)
      let boldRegex = /\*\*(.*?)\*\*/g;
      let lastIndex = 0;
      let match;
      
      while ((match = boldRegex.exec(content)) !== null) {
        // Add text before the bold part
        if (match.index > lastIndex) {
          formattedTexts.push({
            type: "text",
            text: { content: content.substring(lastIndex, match.index) }
          });
        }
        
        // Add the bold text
        formattedTexts.push({
          type: "text",
          text: { content: match[1] },
          annotations: { bold: true }
        });
        
        lastIndex = match.index + match[0].length;
      }
      
      // Add remaining text
      if (lastIndex < content.length) {
        formattedTexts.push({
          type: "text",
          text: { content: content.substring(lastIndex) }
        });
      }
      
      // If no formatting was found, use the original text
      if (formattedTexts.length === 0) {
        formattedTexts.push({
          type: "text",
          text: { content }
        });
      }
      
      blocks.push({
        object: "block",
        type: "paragraph",
        paragraph: {
          rich_text: formattedTexts
        }
      });
    } else if (line.length === 0 && blocks.length > 0) {
      // Empty line - add a spacer if not at the beginning
      blocks.push({
        object: "block",
        type: "paragraph",
        paragraph: {
          rich_text: []
        }
      });
    }
    
    i++;
  }
  
  return blocks;
}

// Function to find doctor ID by name
async function findDoctorByName(name) {
  try {
    const response = await notion.databases.query({
      database_id: DATABASES.MEDICAL_TEAM,
      filter: {
        property: "Name",
        title: {
          contains: name,
        },
      },
    });
    
    if (response.results.length > 0) {
      return response.results[0].id;
    }
    
    return null;
  } catch (error) {
    console.error(`Error finding doctor: ${name}`, error);
    return null;
  }
}

// Function to create a new doctor in the Medical Team database
async function createDoctor(name, specialty = null) {
  try {
    const response = await notion.pages.create({
      parent: {
        database_id: DATABASES.MEDICAL_TEAM,
      },
      properties: {
        Name: {
          title: [
            {
              text: {
                content: name,
              },
            },
          ],
        },
        Specialty: specialty ? {
          select: {
            name: specialty,
          },
        } : undefined,
      },
    });
    
    console.log(`Created doctor: ${name}`);
    return response.id;
  } catch (error) {
    console.error(`Error creating doctor: ${name}`, error);
    return null;
  }
}

// Main function to process and import lab results
async function importLabResults() {
  const extractedTextsDir = path.join(__dirname, '../data/extracted_text');
  const fileContents = await readExtractedFiles(extractedTextsDir);
  
  for (const [filename, content] of Object.entries(fileContents)) {
    // Skip non-lab files for now
    if (!filename.includes('TSH') && !filename.includes('THYROID') && 
        !filename.includes('METABOLIC') && !filename.includes('LIPID') &&
        !filename.includes('CBC') && !filename.includes('HEMOGLOBIN') &&
        !filename.includes('VITAMIN') && !filename.includes('IRON') &&
        !filename.includes('ANTIBODY') && !filename.includes('RHEUMATOID')) {
      continue;
    }
    
    console.log(`Processing file: ${filename}`);
    
    // Parse test date from file content or filename
    let date = null;
    const parsedResult = parseLabResult(content);
    
    if (parsedResult.testDate) {
      date = parsedResult.testDate;
    } else if (parsedResult.resultDate) {
      date = parsedResult.resultDate;
    } else {
      date = parseDateFromFilename(filename);
    }
    
    if (!date) {
      console.log(`Skipping file with no date: ${filename}`);
      continue;
    }
    
    // Extract doctor name from content or filename
    let doctorName = null;
    if (parsedResult.provider) {
      doctorName = parsedResult.provider;
    } else {
      const filenameDoctorName = parseDoctorFromFilename(filename);
      if (filenameDoctorName) {
        doctorName = `Dr. ${filenameDoctorName}`;
      }
    }
    
    if (!doctorName) {
      console.log(`No doctor found for file: ${filename}, using "Unknown Provider"`);
      doctorName = "Unknown Provider";
    }
    
    // Extract test name from parsed result or filename
    let testName = null;
    if (parsedResult.testName) {
      testName = parsedResult.testName;
    } else {
      // Extract from filename
      const testType = extractTestType(filename);
      testName = testType;
    }
    
    if (!testName) {
      testName = "Unknown Test";
    }
    
    // Format title according to standards
    const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
    const title = `${testName} - ${formattedDate}`;
    
    // Find or create doctor
    let doctorId = await findDoctorByName(doctorName);
    if (!doctorId) {
      doctorId = await createDoctor(doctorName);
    }
    
    // Check for relevant diagnoses based on test type
    const diagnosisMapping = {
      'Thyroid Function': 'Graves Disease',
      'Rheumatology Panel': 'Rheumatoid Arthritis',
      'Vitamin Levels': 'Vitamin Deficiency',
    };
    
    // Get diagnosis IDs if applicable
    const diagnosisIds = [];
    const relevantDiagnosis = diagnosisMapping[extractTestType(filename)];
    
    if (relevantDiagnosis) {
      try {
        const response = await notion.databases.query({
          database_id: DATABASES.DIAGNOSES,
          filter: {
            property: "Name",
            title: {
              contains: relevantDiagnosis,
            },
          },
        });
        
        if (response.results.length > 0) {
          diagnosisIds.push(response.results[0].id);
        }
      } catch (error) {
        console.error(`Error finding diagnosis: ${relevantDiagnosis}`, error);
      }
    }
    
    if (doctorId) {
      const labInfo = {
        title,
        date,
        doctorId,
        content,
        parsedData: parsedResult,
        diagnosisIds
      };
      
      await addLabResultToNotion(labInfo);
    }
  }
}

// Function to import doctor appointment notes
async function importAppointmentNotes() {
  // Similar implementation as lab results
  // Will implement in next phase
  console.log("Appointment notes import not yet implemented");
}

// Function to import diagnoses
async function importDiagnoses() {
  // Similar implementation as lab results
  // Will implement in next phase
  console.log("Diagnoses import not yet implemented");
}

// Function to import medications
async function importMedications() {
  // Similar implementation as lab results
  // Will implement in next phase
  console.log("Medications import not yet implemented");
}

// Execute the import functions
async function runImports() {
  try {
    console.log("Starting import process...");
    
    console.log("Importing lab results...");
    await importLabResults();
    
    console.log("Import completed successfully");
  } catch (error) {
    console.error("Import failed:", error);
  }
}

// Check if running directly (not imported)
if (require.main === module) {
  runImports();
} 