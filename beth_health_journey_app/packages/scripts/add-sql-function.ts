import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';

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

async function createSQLFunction() {
  try {
    console.log('Creating SQL execution function...');
    
    // SQL to create a function that can execute arbitrary SQL
    const createFunctionSQL = `
    CREATE OR REPLACE FUNCTION exec_sql(sql_query text)
    RETURNS void
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
      EXECUTE sql_query;
    END;
    $$;
    `;
    
    // Execute the SQL to create the function
    const { data, error } = await supabase.rpc('exec_sql', { sql_query: createFunctionSQL });
    
    if (error) {
      if (error.message.includes('function "exec_sql" does not exist')) {
        console.log('Function does not exist yet. Creating it with raw SQL...');
        
        // Try using raw SQL if the function doesn't exist yet
        const { error: rawError } = await supabase.from('rpc').select('*').eq('name', 'exec_sql');
        
        if (rawError) {
          console.error('Error checking for existing function:', rawError.message);
          console.log('Unable to create the function automatically. Use the Supabase SQL editor to run:');
          console.log(createFunctionSQL);
        } else {
          console.log('Function exists or was created successfully.');
        }
      } else {
        throw error;
      }
    } else {
      console.log('Function created successfully!');
    }

    // Also create a function specifically for creating the medical_event_symptoms table
    const createTableFunctionSQL = `
    CREATE OR REPLACE FUNCTION create_medical_event_symptoms_table()
    RETURNS void
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
      -- Create the table
      CREATE TABLE IF NOT EXISTS public.medical_event_symptoms (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        medical_event_id UUID REFERENCES public.medical_events(id) ON DELETE CASCADE,
        symptom_id UUID REFERENCES public.symptoms(id) ON DELETE CASCADE,
        severity INTEGER CHECK (severity >= 1 AND severity <= 10),
        notes TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid()
      );
      
      -- Create indexes
      CREATE INDEX IF NOT EXISTS idx_medical_event_symptoms_medical_event_id ON public.medical_event_symptoms(medical_event_id);
      CREATE INDEX IF NOT EXISTS idx_medical_event_symptoms_symptom_id ON public.medical_event_symptoms(symptom_id);
      
      -- Enable RLS
      ALTER TABLE public.medical_event_symptoms ENABLE ROW LEVEL SECURITY;
      
      -- Create policies
      CREATE POLICY IF NOT EXISTS "Users can view their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR SELECT
        USING (auth.uid() = user_id);
      
      CREATE POLICY IF NOT EXISTS "Users can insert their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
      
      CREATE POLICY IF NOT EXISTS "Users can update their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR UPDATE
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
      
      CREATE POLICY IF NOT EXISTS "Users can delete their own medical event symptoms"
        ON public.medical_event_symptoms
        FOR DELETE
        USING (auth.uid() = user_id);
    END;
    $$;
    `;
    
    // Try to create the table function
    const { error: tableFnError } = await supabase.rpc('exec_sql', { sql_query: createTableFunctionSQL });
    
    if (tableFnError) {
      console.error('Error creating table function:', tableFnError.message);
      console.log('You may need to run this SQL in the Supabase SQL editor:');
      console.log(createTableFunctionSQL);
    } else {
      console.log('Table creation function created successfully!');
    }
    
    console.log('Process completed.');
    
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error creating SQL function:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  }
}

// Run the function
createSQLFunction().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
}); 