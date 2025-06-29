require('dotenv').config();
const { Client } = require('@notionhq/client');

// Initialize the Notion client
const notion = new Client({ auth: process.env.NOTION_TOKEN });
const DATABASE_ID = process.env.THERAPIST_DB_ID || '1d586edcae2c8035b63ac880990ace27';

async function checkDatabaseAccess() {
  try {
    console.log('Checking Notion database access...');
    
    // Retrieve database information
    const database = await notion.databases.retrieve({ database_id: DATABASE_ID });
    
    console.log('\n✅ Successfully connected to Notion database!');
    console.log(`Database Name: ${database.title[0]?.plain_text || 'Untitled'}`);
    console.log(`Database ID: ${DATABASE_ID}`);
    
    // Display database schema/properties
    console.log('\nDatabase Schema:');
    console.log('----------------');
    
    const properties = database.properties;
    Object.keys(properties).forEach(key => {
      const property = properties[key];
      console.log(`${key} (${property.type})`);
      
      // Display additional details for specific property types
      if (property.type === 'select' || property.type === 'status') {
        console.log('  Options:');
        const options = property.select?.options || property.status?.options || [];
        options.forEach(option => {
          console.log(`    - ${option.name} ${option.color ? `(${option.color})` : ''}`);
        });
      } else if (property.type === 'multi_select') {
        console.log('  Options:');
        property.multi_select.options.forEach(option => {
          console.log(`    - ${option.name} ${option.color ? `(${option.color})` : ''}`);
        });
      }
    });
    
    // Get sample records
    const response = await notion.databases.query({
      database_id: DATABASE_ID,
      page_size: 3
    });
    
    console.log('\nSample Records:');
    console.log('--------------');
    
    if (response.results.length === 0) {
      console.log('No records found in the database.');
    } else {
      response.results.forEach((page, index) => {
        const title = page.properties.Name?.title[0]?.plain_text || 'Untitled';
        console.log(`${index + 1}. ${title} (${page.id})`);
      });
    }

    return true;
  } catch (error) {
    console.error('\n❌ Error accessing Notion database:');
    console.error(error.message);
    
    if (error.code === 'object_not_found') {
      console.error('\nPossible reasons:');
      console.error('1. The database ID is incorrect');
      console.error('2. Your integration does not have access to this database');
      console.error('\nTo fix:');
      console.error('1. Verify the DATABASE_ID in your code or .env file');
      console.error('2. Make sure you\'ve shared the database with your integration');
      console.error('   (In Notion: Share > Invite > Select your integration)');
    } else if (error.status === 401) {
      console.error('\nAuthentication error:');
      console.error('1. Your NOTION_TOKEN may be invalid or expired');
      console.error('2. Check your .env file and make sure NOTION_TOKEN is set correctly');
    }
    
    return false;
  }
}

// Main function
async function main() {
  const result = await checkDatabaseAccess();
  
  if (!result) {
    console.log('\nFor help setting up your Notion integration:');
    console.log('1. Visit https://developers.notion.com/docs/getting-started');
    console.log('2. Create an integration at https://www.notion.so/my-integrations');
    console.log('3. Share your database with the integration');
    process.exit(1);
  }
}

main(); 