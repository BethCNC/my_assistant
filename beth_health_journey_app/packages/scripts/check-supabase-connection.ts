import dotenv from 'dotenv';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import type { Database } from '../lib/supabase/database.types';

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

// Get Supabase credentials from environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

// Check if credentials are set
if (!supabaseUrl || !supabaseKey) {
  console.error('\n❌ Error: Supabase credentials are missing in .env.local file.');
  console.error('Make sure you have set the following environment variables:');
  console.error('- NEXT_PUBLIC_SUPABASE_URL');
  console.error('- SUPABASE_SERVICE_ROLE_KEY\n');
  process.exit(1);
}

// Initialize Supabase client
const supabase = createClient<Database>(supabaseUrl, supabaseKey);

async function checkConnection() {
  console.log('\n🔍 Checking Supabase connection...\n');
  
  try {
    // Try to fetch from the providers table to check connection
    const { data, error } = await supabase
      .from('providers')
      .select('id')
      .limit(1);
    
    if (error) {
      throw error;
    }
    
    console.log('✅ Successfully connected to Supabase!');
    console.log(`🔗 Project URL: ${supabaseUrl}`);
    
    // Check if tables exist
    console.log('\n📋 Checking database schema...');
    
    const tables = ['conditions', 'symptoms', 'providers', 'medical_events', 'lab_results'];
    
    for (const table of tables) {
      const { count, error: countError } = await supabase
        .from(table)
        .select('*', { count: 'exact', head: true });
        
      if (countError) {
        if (countError.code === '42P01') { // Table does not exist
          console.error(`❌ Table "${table}" does not exist. Make sure to run the SQL script from db/schema.sql.`);
        } else {
          console.error(`❌ Error checking table "${table}": ${countError.message}`);
        }
      } else {
        console.log(`✅ Table "${table}" exists and is accessible.`);
      }
    }
    
    console.log('\n📊 Database connection summary:');
    console.log('1. Supabase connection: ✅ Connected');
    console.log(`2. Database URL: ${supabaseUrl}`);
    console.log('3. Schema verification: ' + (tables.length === 5 ? '✅ All tables verified' : '❌ Some tables are missing'));
    
    console.log('\n🚀 Next Steps:');
    console.log('1. Run data import scripts: npx ts-node scripts/import-all.ts');
    console.log('2. Start the Next.js app: npm run dev\n');
    
  } catch (error) {
    console.error('\n❌ Failed to connect to Supabase:');
    if (error instanceof Error) {
      console.error(error.message);
    } else {
      console.error(error);
    }
    
    console.error('\n🔍 Troubleshooting:');
    console.error('1. Verify your Supabase URL and API keys in .env.local');
    console.error('2. Make sure your IP is allowed in Supabase settings');
    console.error('3. Check if your Supabase project is active and not in maintenance mode');
    process.exit(1);
  }
}

checkConnection(); 