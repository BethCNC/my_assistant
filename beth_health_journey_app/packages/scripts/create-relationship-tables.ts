import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import readline from 'readline';

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

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to prompt for user input
function askQuestion(question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

async function createRelationshipTables() {
  try {
    console.log('Checking if the medical_event_symptoms table exists...');

    // Check if medical_event_symptoms table exists
    const { error: tableCheckError } = await supabase
      .from('medical_event_symptoms')
      .select('id')
      .limit(1);

    if (tableCheckError && tableCheckError.message.includes('relation "public.medical_event_symptoms" does not exist')) {
      console.log('The medical_event_symptoms table does not exist. We need to create it.');
      
      // SQL file path
      const sqlFilePath = path.resolve(process.cwd(), 'scripts/create_medical_event_symptoms.sql');
      console.log(`Reading SQL from: ${sqlFilePath}`);
      const sql = fs.readFileSync(sqlFilePath, 'utf8');
      
      // Show SQL to user
      console.log('\nHere is the SQL that will create the table:');
      console.log('----------------------------------------');
      console.log(sql);
      console.log('----------------------------------------\n');
      
      // Ask user to confirm
      const confirmCreate = await askQuestion('Would you like me to guide you to create this table? (y/n): ');
      
      if (confirmCreate.toLowerCase() === 'y') {
        console.log('\nSince we cannot execute SQL directly through the JavaScript API, I will guide you:');
        console.log('\n1. Go to your Supabase dashboard (https://app.supabase.com)');
        console.log('2. Select your project');
        console.log('3. Click on "SQL Editor" in the left menu');
        console.log('4. Create a "New query"');
        console.log('5. Paste the SQL shown above into the editor');
        console.log('6. Click "Run" to execute the SQL');
        console.log('\nAfter you have created the table, press Enter to continue...');
        
        await askQuestion('');
        
        // Check if table exists now
        const { error: secondCheckError } = await supabase
          .from('medical_event_symptoms')
          .select('id')
          .limit(1);
        
        if (secondCheckError && secondCheckError.message.includes('relation "public.medical_event_symptoms" does not exist')) {
          console.log('\nThe table still does not exist. Did you complete the steps?');
          console.log('Let\'s continue anyway and you can retry later if needed.');
        } else {
          console.log('\nGreat! The medical_event_symptoms table exists now.');
        }
      } else {
        console.log('Table creation skipped.');
      }
    } else {
      console.log('The medical_event_symptoms table already exists!');
    }
    
    // Ask if user wants to link symptoms to events
    const linkSymptoms = await askQuestion('\nWould you like to link symptoms to medical events? (y/n): ');
    
    if (linkSymptoms.toLowerCase() === 'y') {
      await linkSymptomsToEvents();
    } else {
      console.log('Symptom linking skipped.');
    }
    
    console.log('\nProcess completed.');
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error creating relationship tables:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  } finally {
    rl.close();
  }
}

async function linkSymptomsToEvents() {
  try {
    console.log('\nStarting to link symptoms to medical events...');

    // Check if medical_event_symptoms table exists
    const { error: tableCheckError } = await supabase
      .from('medical_event_symptoms')
      .select('id')
      .limit(1);

    if (tableCheckError && tableCheckError.message.includes('relation "public.medical_event_symptoms" does not exist')) {
      console.error('Error: The medical_event_symptoms table does not exist.');
      console.log('Please create the table first using the SQL from scripts/create_medical_event_symptoms.sql');
      return;
    }

    // Fetch all symptoms
    const { data: symptoms, error: symptomsError } = await supabase
      .from('symptoms')
      .select('id, name, description, severity')
      .order('name');

    if (symptomsError) throw symptomsError;
    if (!symptoms || symptoms.length === 0) {
      console.log('No symptoms found in the database.');
      return;
    }

    console.log(`Found ${symptoms.length} symptoms.`);

    // Fetch recent medical events (last 30)
    const { data: events, error: eventsError } = await supabase
      .from('medical_events')
      .select('id, title, date, event_type')
      .order('date', { ascending: false })
      .limit(30);

    if (eventsError) throw eventsError;
    if (!events || events.length === 0) {
      console.log('No medical events found in the database.');
      return;
    }

    console.log(`Found ${events.length} recent medical events.`);

    console.log('\n==== Medical Events ====');
    events.forEach((event, index) => {
      const date = new Date(event.date).toLocaleDateString();
      console.log(`[${index + 1}] ${event.title} (${date}) - ${event.event_type}`);
    });

    const eventIndexStr = await askQuestion('\nSelect an event by number (1-30): ');
    const eventIndex = parseInt(eventIndexStr, 10) - 1;
    
    if (isNaN(eventIndex) || eventIndex < 0 || eventIndex >= events.length) {
      console.log('Invalid event selection. Operation cancelled.');
      return;
    }

    const selectedEvent = events[eventIndex];
    console.log(`\nSelected event: ${selectedEvent.title}`);

    console.log('\n==== Available Symptoms ====');
    symptoms.forEach((symptom, index) => {
      console.log(`[${index + 1}] ${symptom.name}`);
    });

    const symptomIndicesStr = await askQuestion('\nSelect symptom numbers to link (comma separated, e.g. 1,3,5): ');
    const symptomIndices = symptomIndicesStr.split(',').map(index => parseInt(index.trim(), 10) - 1);
    
    const selectedSymptoms = [];
    
    for (const index of symptomIndices) {
      if (isNaN(index) || index < 0 || index >= symptoms.length) {
        console.log(`Skipping invalid symptom selection: ${index + 1}`);
      } else {
        selectedSymptoms.push(symptoms[index]);
      }
    }

    if (selectedSymptoms.length === 0) {
      console.log('No valid symptoms selected. Operation cancelled.');
      return;
    }

    console.log(`\nSelected symptoms: ${selectedSymptoms.map(s => s.name).join(', ')}`);
    const confirmLink = await askQuestion('\nConfirm linking these symptoms to the selected event? (y/n): ');
    
    if (confirmLink.toLowerCase() !== 'y') {
      console.log('Operation cancelled.');
      return;
    }

    console.log('\nLinking symptoms to event...');
    
    // Create links for each selected symptom
    const links = [];
    
    for (const symptom of selectedSymptoms) {
      const severityStr = await askQuestion(`Severity for ${symptom.name} (1-10, optional): `);
      const severity = severityStr ? parseInt(severityStr, 10) : null;
      
      const notes = await askQuestion(`Notes for ${symptom.name} (optional): `);
      
      links.push({
        medical_event_id: selectedEvent.id,
        symptom_id: symptom.id,
        severity: severity && !isNaN(severity) && severity >= 1 && severity <= 10 ? severity : null,
        notes: notes || null
      });
    }

    // Insert links into medical_event_symptoms table
    const { data: insertResult, error: insertError } = await supabase
      .from('medical_event_symptoms')
      .insert(links);

    if (insertError) {
      throw insertError;
    }

    console.log(`Successfully linked ${links.length} symptoms to the medical event!`);

    // Verify the links
    const { data: verifyLinks, error: verifyError } = await supabase
      .from('medical_event_symptoms')
      .select('*, symptoms(name)')
      .eq('medical_event_id', selectedEvent.id);

    if (verifyError) {
      console.warn('Warning: Could not verify links:', verifyError.message);
    } else {
      console.log(`\nVerified ${verifyLinks?.length || 0} links for this medical event.`);
    }

  } catch (error) {
    if (error instanceof Error) {
      console.error('Error linking symptoms to events:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  }
}

// Run the function
createRelationshipTables().catch((error) => {
  console.error('Fatal error:', error);
  rl.close();
  process.exit(1);
}); 