import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

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

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Read the SQL migration file
const migrationPath = path.resolve(process.cwd(), 'supabase/migrations/20240409_create_medical_event_symptoms_table.sql');
const sql = fs.readFileSync(migrationPath, 'utf8');

async function createMedicalEventSymptomsTable() {
  try {
    console.log('Creating medical_event_symptoms table...');
    
    // Execute the SQL commands
    const { error } = await supabase.rpc('exec_sql', { sql_query: sql });
    
    if (error) {
      if (error.message.includes('function "exec_sql" does not exist')) {
        console.error('Error: The exec_sql function does not exist in your Supabase instance.');
        console.log('Creating a simple version of the table instead...');
        
        // Create a simplified version if the RPC function doesn't exist
        const { error: createError } = await supabase.rpc('create_medical_event_symptoms_table');
        
        if (createError) {
          if (createError.message.includes('function "create_medical_event_symptoms_table" does not exist')) {
            console.log('Attempting direct SQL execution...');
            
            // Try direct table creation if the function doesn't exist
            const { error: directError } = await supabase.from('medical_event_symptoms').select('id').limit(1);
            
            if (directError && directError.message.includes('relation "public.medical_event_symptoms" does not exist')) {
              await executeMigrationManually();
            } else if (!directError) {
              console.log('Table already exists!');
            } else {
              throw directError;
            }
          } else {
            throw createError;
          }
        } else {
          console.log('Table created successfully using create_medical_event_symptoms_table function!');
        }
      } else {
        throw error;
      }
    } else {
      console.log('SQL executed successfully!');
    }
    
    // Verify the table exists
    const { data, error: verifyError } = await supabase
      .from('medical_event_symptoms')
      .select('id')
      .limit(1);
      
    if (verifyError) {
      console.error('Error verifying table creation:', verifyError.message);
    } else {
      console.log('Table verified to exist!');
    }
    
    console.log('Process completed.');
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error creating table:', error.message);
    } else {
      console.error('Unknown error creating table:', error);
    }
  }
}

async function executeMigrationManually() {
  console.log('Executing migration manually...');
  
  try {
    // Create the table with basic structure
    const createTableSQL = `
    CREATE TABLE IF NOT EXISTS public.medical_event_symptoms (
      id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
      medical_event_id UUID REFERENCES public.medical_events(id) ON DELETE CASCADE,
      symptom_id UUID REFERENCES public.symptoms(id) ON DELETE CASCADE,
      severity INTEGER CHECK (severity >= 1 AND severity <= 10),
      notes TEXT,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW(),
      user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid()
    );`;
    
    // Create table
    const { error: createError } = await supabase.rpc('exec_sql', { sql_query: createTableSQL });
    
    if (createError) {
      if (createError.message.includes('function "exec_sql" does not exist')) {
        console.error('Cannot execute SQL directly. Please run the migration manually.');
      } else {
        throw createError;
      }
    } else {
      console.log('Table created!');
      
      // Create indexes
      const indexSQL = `
      CREATE INDEX IF NOT EXISTS idx_medical_event_symptoms_medical_event_id ON public.medical_event_symptoms(medical_event_id);
      CREATE INDEX IF NOT EXISTS idx_medical_event_symptoms_symptom_id ON public.medical_event_symptoms(symptom_id);
      `;
      
      const { error: indexError } = await supabase.rpc('exec_sql', { sql_query: indexSQL });
      
      if (indexError) {
        console.error('Error creating indexes:', indexError.message);
      } else {
        console.log('Indexes created!');
      }
      
      // Enable RLS
      const rlsSQL = `ALTER TABLE public.medical_event_symptoms ENABLE ROW LEVEL SECURITY;`;
      
      const { error: rlsError } = await supabase.rpc('exec_sql', { sql_query: rlsSQL });
      
      if (rlsError) {
        console.error('Error enabling RLS:', rlsError.message);
      } else {
        console.log('RLS enabled!');
      }
      
      // Create policies
      const policiesSQL = `
      CREATE POLICY "Users can view their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR SELECT
        USING (auth.uid() = user_id);
      
      CREATE POLICY "Users can insert their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
      
      CREATE POLICY "Users can update their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR UPDATE
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
      
      CREATE POLICY "Users can delete their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR DELETE
        USING (auth.uid() = user_id);
      `;
      
      const { error: policiesError } = await supabase.rpc('exec_sql', { sql_query: policiesSQL });
      
      if (policiesError) {
        console.error('Error creating policies:', policiesError.message);
      } else {
        console.log('Policies created!');
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error in manual migration:', error.message);
    } else {
      console.error('Unknown error in manual migration:', error);
    }
  }
}

// Run the function
createMedicalEventSymptomsTable().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
}); 