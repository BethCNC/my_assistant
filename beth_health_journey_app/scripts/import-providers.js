const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');
const csv = require('csv-parser');
require('dotenv').config();

// Constants
const CSV_FILE = path.join(process.cwd(), 'medical_team.csv');

// Notion database IDs
const NOTION_MEDICAL_TEAM_DB = '17b86edc-ae2c-8155-8caa-fbb80647f6a9';

// Configure Supabase
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Parse CSV and extract provider data
async function parseProvidersCSV() {
  const providers = [];
  
  return new Promise((resolve, reject) => {
    fs.createReadStream(CSV_FILE)
      .pipe(csv({
        // Handle quoted fields properly
        quote: '"',
        escape: '"'
      }))
      .on('data', (row) => {
        // Get column values (adjust these based on your CSV structure)
        const provider = {
          name: row['Name'] || row[0] || '',
          specialty: row['Specialty'] || row[1] || '',
          facility: row['Facility'] || row[2] || '',
          startDate: row['Start Date'] || row[3] || '',
          conditions: (row['Conditions'] || row[4] || '').split(',').map(c => c.trim()),
          address: row['Address'] || row[5] || '',
          phone: row['Phone'] || row[6] || '',
          email: row['Email'] || row[7] || '',
          website: row['Website'] || row[8] || '',
          notes: row['Notes'] || row[11] || '',
          status: row['Status'] || row[12] || 'Active'
        };
        
        providers.push(provider);
      })
      .on('end', () => {
        console.log(`Parsed ${providers.length} providers from CSV`);
        resolve(providers);
      })
      .on('error', (error) => {
        reject(error);
      });
  });
}

// Add provider to Supabase
async function addProviderToSupabase(provider) {
  try {
    // Check if provider already exists
    const { data: existingProviders } = await supabase
      .from('providers')
      .select('*')
      .ilike('name', `%${provider.name}%`)
      .limit(1);
      
    if (existingProviders && existingProviders.length > 0) {
      console.log(`Provider already exists in Supabase: ${provider.name}`);
      
      // Update provider
      const { data: updatedProvider, error } = await supabase
        .from('providers')
        .update({
          specialty: provider.specialty,
          facility: provider.facility,
          address: provider.address,
          phone: provider.phone,
          email: provider.email,
          website: provider.website,
          notes: provider.notes,
          updated_at: new Date().toISOString()
        })
        .eq('id', existingProviders[0].id)
        .select();
        
      if (error) {
        console.error(`Error updating provider in Supabase: ${error.message}`);
        return null;
      }
      
      console.log(`Updated provider in Supabase: ${updatedProvider[0].id}`);
      return updatedProvider[0].id;
    }
    
    // Create new provider
    const { data: newProvider, error } = await supabase
      .from('providers')
      .insert({
        name: provider.name,
        specialty: provider.specialty,
        facility: provider.facility,
        address: provider.address,
        phone: provider.phone,
        email: provider.email,
        website: provider.website,
        notes: provider.notes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .select();
      
    if (error) {
      console.error(`Error creating provider in Supabase: ${error.message}`);
      return null;
    }
    
    console.log(`Added provider to Supabase: ${newProvider[0].id}`);
    return newProvider[0].id;
  } catch (error) {
    console.error(`Error adding provider to Supabase: ${error.message}`);
    return null;
  }
}

// Add provider to Notion
async function addProviderToNotion(provider) {
  try {
    // Check if provider already exists
    const response = await global.mcp_notion_notion_query_database({
      database_id: NOTION_MEDICAL_TEAM_DB,
      filter: {
        property: "Name",
        title: {
          contains: provider.name
        }
      },
      page_size: 1
    });
    
    const result = JSON.parse(response);
    
    if (result.results && result.results.length > 0) {
      console.log(`Provider already exists in Notion: ${provider.name}`);
      return result.results[0].id;
    }
    
    // Create properties for Notion
    const properties = {
      "Name": {
        "title": [
          {
            "text": {
              "content": provider.name
            }
          }
        ]
      },
      "Specialty": {
        "rich_text": [
          {
            "text": {
              "content": provider.specialty
            }
          }
        ]
      },
      "Facility": {
        "rich_text": [
          {
            "text": {
              "content": provider.facility
            }
          }
        ]
      }
    };
    
    // Add address if available
    if (provider.address) {
      properties["Address"] = {
        "rich_text": [
          {
            "text": {
              "content": provider.address
            }
          }
        ]
      };
    }
    
    // Add phone if available
    if (provider.phone) {
      properties["Phone"] = {
        "rich_text": [
          {
            "text": {
              "content": provider.phone
            }
          }
        ]
      };
    }
    
    // Add email if available
    if (provider.email) {
      properties["Email"] = {
        "rich_text": [
          {
            "text": {
              "content": provider.email
            }
          }
        ]
      };
    }
    
    // Add website if available
    if (provider.website) {
      properties["Website"] = {
        "rich_text": [
          {
            "text": {
              "content": provider.website
            }
          }
        ]
      };
    }
    
    // Add notes if available
    if (provider.notes) {
      properties["Notes"] = {
        "rich_text": [
          {
            "text": {
              "content": provider.notes
            }
          }
        ]
      };
    }
    
    // Create provider in Notion
    const createResponse = await global.mcp_notion_notion_create_database_item({
      database_id: NOTION_MEDICAL_TEAM_DB,
      properties: properties
    });
    
    const createResult = JSON.parse(createResponse);
    console.log(`Added provider to Notion: ${createResult.id}`);
    
    return createResult.id;
  } catch (error) {
    console.error(`Error adding provider to Notion: ${error.message}`);
    return null;
  }
}

// Main function
async function main() {
  console.log("Starting provider import process...");
  
  // Validate environment
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    console.error("Supabase credentials not found in environment variables");
    process.exit(1);
  }
  
  // Check for MCP Notion integration
  if (!global.mcp_notion_notion_query_database || !global.mcp_notion_notion_create_database_item) {
    console.warn("MCP Notion functions not available. Will only update Supabase.");
  }
  
  try {
    // Parse providers from CSV
    const providers = await parseProvidersCSV();
    
    // Process each provider
    for (const provider of providers) {
      console.log(`Processing provider: ${provider.name}`);
      
      // Add to Supabase
      const supabaseId = await addProviderToSupabase(provider);
      
      // Add to Notion if MCP integration is available
      if (global.mcp_notion_notion_query_database && global.mcp_notion_notion_create_database_item) {
        const notionId = await addProviderToNotion(provider);
      }
    }
    
    console.log("Provider import complete!");
  } catch (error) {
    console.error(`Error during provider import: ${error.message}`);
    process.exit(1);
  }
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

// Run the script
main().catch(console.error); 