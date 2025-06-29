import fs from 'fs';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function setupSupabaseSchema() {
  // Check if schema file exists
  const schemaFile = path.resolve(process.cwd(), 'db/schema.sql');
  if (!fs.existsSync(schemaFile)) {
    console.error('\n❌ Schema file not found. Make sure db/schema.sql exists.');
    process.exit(1);
  }

  // Read schema file
  const sqlContent = fs.readFileSync(schemaFile, 'utf8');
  const sqlStatements = sqlContent
    .split(/;\s*$/m) // Split on semicolons at the end of lines
    .filter(sql => sql.trim().length > 0); // Remove empty statements

  // Get Supabase credentials
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    console.error('\n❌ Supabase credentials are missing. Please update your .env.local file.');
    process.exit(1);
  }

  console.log('\n🔧 Setting up Supabase schema...');
  console.log(`📑 Found ${sqlStatements.length} SQL statements to execute.`);
  console.log('\n⚠️ IMPORTANT: This is a guide for manual setup. ⚠️');
  console.log('Supabase does not support direct SQL execution via the API for complex schemas.');
  console.log('Please follow these instructions instead:');
  console.log('\n1. Log in to your Supabase dashboard');
  console.log('2. Go to "SQL Editor" from the left sidebar');
  console.log('3. Click "+ New Query" and paste the entire contents of db/schema.sql');
  console.log('4. Click "Run" to execute the SQL and create your schema');
  
  // Print the first few statements as a preview
  console.log('\n📋 Preview of the SQL schema (first 3 statements):');
  for (let i = 0; i < Math.min(3, sqlStatements.length); i++) {
    console.log(`\n--- Statement ${i+1} ---\n${sqlStatements[i].trim().substring(0, 200)}${sqlStatements[i].length > 200 ? '...' : ''}`);
  }
  
  console.log('\n🧪 After running the SQL in Supabase dashboard, verify your setup:');
  console.log('Run: npx ts-node scripts/check-supabase-connection.ts');
  
  // Create a file with Supabase SQL commands for easy copy/paste
  const setupInstructionsFile = path.resolve(process.cwd(), 'db/setup-instructions.md');
  
  const instructions = `# Supabase Setup Instructions

## 1. SQL Schema

Log in to your Supabase dashboard, go to the SQL Editor, and run the following SQL:

\`\`\`sql
${sqlContent}
\`\`\`

## 2. Verify Setup

After running the SQL, go back to your terminal and run:

\`\`\`bash
npx ts-node scripts/check-supabase-connection.ts
\`\`\`

## 3. Import Data

Once the schema is created and verified, import your data:

\`\`\`bash
npx ts-node scripts/import-all.ts
\`\`\`
`;
  
  fs.writeFileSync(setupInstructionsFile, instructions);
  console.log(`\n✅ Created setup instructions file at: db/setup-instructions.md`);
  console.log('You can open this file for easy copy/paste into the Supabase SQL Editor.');
}

setupSupabaseSchema(); 