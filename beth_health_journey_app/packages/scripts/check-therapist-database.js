require('dotenv').config();
const { Client } = require('@notionhq/client');

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

// Database ID from the therapist-rules.mdc
const databaseId = '1d586edcae2c8035b63ac880990ace27';

async function checkTherapistDatabase() {
  try {
    // First, check if the database exists
    console.log(`Attempting to access Therapist database with ID: ${databaseId}`);
    const database = await notion.databases.retrieve({
      database_id: databaseId,
    });
    
    console.log(`Successfully accessed database: ${database.title[0]?.plain_text || 'Unnamed Database'}`);
    
    // Check the database schema
    console.log('\nDatabase Properties:');
    const properties = database.properties;
    for (const [key, value] of Object.entries(properties)) {
      console.log(`- ${key} (${value.type})`);
    }
    
    // Query for existing entries
    console.log('\nQuerying existing entries...');
    const response = await notion.databases.query({
      database_id: databaseId,
      page_size: 50, // Increased from 10 to 50 entries
    });
    
    console.log(`Found ${response.results.length} entries out of ${response.has_more ? '50+' : response.results.length} total`);
    
    // List existing entries
    if (response.results.length > 0) {
      console.log('\nExisting entries:');
      for (const page of response.results) {
        const title = page.properties.Name?.title[0]?.plain_text || 'Unnamed';
        const group = page.properties['Office/Group']?.multi_select?.map(item => item.name).join(', ') || 'No group';
        console.log(`- ${title} (${group})`);
      }
    }
    
    return {
      success: true,
      database,
      entries: response.results,
    };
  } catch (error) {
    console.error('Error accessing Notion database:', error.message);
    
    if (error.code === 'object_not_found') {
      console.error(`\nThe database with ID ${databaseId} was not found.`);
      console.error('Please check that the database ID is correct and that your integration has access to it.');
    }
    
    if (error.status === 401) {
      console.error('\nAuthorization error: Your Notion token may be invalid or expired.');
      console.error('Check your NOTION_TOKEN in the .env file.');
    }
    
    return {
      success: false,
      error,
    };
  }
}

// Execute the check
checkTherapistDatabase()
  .then(result => {
    if (result.success) {
      console.log('\nDatabase check completed successfully.');
    } else {
      console.error('\nDatabase check failed.');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('Unexpected error:', error);
    process.exit(1);
  }); 