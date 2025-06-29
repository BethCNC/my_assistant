import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import readline from 'readline';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Supabase client with admin permissions
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

interface Symptom {
  id: string;
  name: string;
}

interface MedicalEvent {
  id: string;
  title: string;
  date: string;
  event_type: string;
}

interface SymptomLink {
  id: string;
  symptom_id: string;
  severity: number | null;
  notes: string | null;
  symptoms: {
    name: string;
  };
}

async function linkSymptomsToEvents() {
  try {
    console.log('Starting symptom linking process...');

    // Verify table exists and is accessible
    console.log('Checking if the relationship table exists...');
    const { error: tableCheckError } = await supabase
      .from('medical_event_symptoms')
      .select('id')
      .limit(1);

    if (tableCheckError) {
      console.error('Error accessing the medical_event_symptoms table:', tableCheckError.message);
      return;
    }

    console.log('Table is accessible! Now fetching symptoms and events...');

    // Fetch all symptoms
    const { data: symptomsData, error: symptomsError } = await supabase
      .from('symptoms')
      .select('*')
      .order('name');

    if (symptomsError) {
      console.error('Error fetching symptoms:', symptomsError.message);
      return;
    }

    if (!symptomsData || symptomsData.length === 0) {
      console.error('No symptoms found in the database');
      console.log('Debug symptoms response:', JSON.stringify(symptomsData, null, 2));
      return;
    }

    // Debug: Log structure of first symptom
    console.log('Debug - First symptom structure:', JSON.stringify(symptomsData[0], null, 2));

    const symptoms = symptomsData as Symptom[];

    console.log(`Found ${symptoms.length} symptoms.`);

    // Fetch recent medical events
    const { data: events, error: eventsError } = await supabase
      .from('medical_events')
      .select('id, title, date, event_type')
      .order('date', { ascending: false })
      .limit(30);

    if (eventsError) {
      console.error('Error fetching events:', eventsError.message);
      return;
    }

    if (!events || events.length === 0) {
      console.log('No medical events found in the database.');
      return;
    }

    console.log(`Found ${events.length} recent medical events.`);

    // Display events
    console.log('\n===== MEDICAL EVENTS =====');
    events.forEach((event, index) => {
      const date = new Date(event.date).toLocaleDateString();
      console.log(`[${index + 1}] ${event.title} (${date}) - ${event.event_type}`);
    });

    // Select event
    const eventIndexStr = await askQuestion('\nSelect an event by number (1-30): ');
    const eventIndex = parseInt(eventIndexStr, 10) - 1;
    
    if (isNaN(eventIndex) || eventIndex < 0 || eventIndex >= events.length) {
      console.log('Invalid event selection. Operation cancelled.');
      return;
    }

    const selectedEvent = events[eventIndex];
    console.log(`\nSelected event: ${selectedEvent.title}`);

    // Display symptoms
    console.log('\n===== AVAILABLE SYMPTOMS =====');
    symptoms.forEach((symptom, index) => {
      console.log(`[${index + 1}] ${symptom.name}`);
    });

    // Select symptoms
    const symptomIndicesStr = await askQuestion('\nSelect symptom numbers to link (comma separated, e.g. 1,3,5): ');
    const symptomIndices = symptomIndicesStr.split(',').map(idx => parseInt(idx.trim(), 10) - 1);
    
    const selectedSymptoms: Symptom[] = [];
    
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
    let successCount = 0;
    
    for (const symptom of selectedSymptoms) {
      const severityStr = await askQuestion(`Severity for ${symptom.name} (1-10, optional): `);
      const severity = severityStr ? parseInt(severityStr, 10) : null;
      
      const notes = await askQuestion(`Notes for ${symptom.name} (optional): `);
      
      const linkData = {
        medical_event_id: selectedEvent.id,
        symptom_id: symptom.id,
        severity: severity && !isNaN(severity) && severity >= 1 && severity <= 10 ? severity : null,
        notes: notes || null
      };
      
      // Insert each link individually to handle potential errors
      const { error: insertError } = await supabase
        .from('medical_event_symptoms')
        .insert([linkData]);
      
      if (insertError) {
        console.error(`Error linking symptom "${symptom.name}":`, insertError.message);
      } else {
        successCount++;
        console.log(`✓ Linked symptom: ${symptom.name}`);
      }
    }

    if (successCount > 0) {
      console.log(`\nSuccessfully linked ${successCount} out of ${selectedSymptoms.length} symptoms to the medical event!`);
    } else {
      console.log('\nFailed to link any symptoms to the medical event.');
    }

    // Verify links
    const verifyLinks = async () => {
      // Get medical events with their linked symptoms
      const { data: events, error: eventsError } = await supabase
        .from('medical_events')
        .select(`
          id, 
          date, 
          event_type,
          symptoms:medical_event_symptoms(
            symptom_id, 
            severity,
            symptoms:symptom_id(id, name)
          )
        `)
        .limit(10);

      if (eventsError) {
        console.error('Error fetching medical events with symptoms:', eventsError.message);
        return;
      }

      if (!events || events.length === 0) {
        console.log('No events found with linked symptoms.');
        return;
      }

      console.log(`Found ${events.length} events. Checking for linked symptoms...`);
      
      // Log the full structure of the first event for debugging
      console.log('DEBUG - First event full structure:', JSON.stringify(events[0], null, 2));

      events.forEach((event) => {
        const links = event.symptoms || [];
        console.log(`Event ID ${event.id} (${event.date}) has ${links.length} linked symptoms:`);
        
        links.forEach((link: any) => {
          try {
            let symptomName = 'Unknown';
            
            // Safely access symptom name with type checking
            if (link.symptoms) {
              if (Array.isArray(link.symptoms) && link.symptoms.length > 0) {
                symptomName = link.symptoms[0].name || 'Unknown';
              } else if (typeof link.symptoms === 'object') {
                symptomName = link.symptoms.name || 'Unknown';
              }
            }
            
            console.log(`- ${symptomName} (Severity: ${link.severity || 'Not specified'})`);
          } catch (err) {
            console.error(`Error accessing symptom data:`, err);
            console.log('Raw link data:', JSON.stringify(link, null, 2));
          }
        });
      });
    };

    await verifyLinks();

    // Check if the medical_event_symptoms table exists and has records
    const { data: relationshipCheck, error: relationshipError } = await supabase
      .from('medical_event_symptoms')
      .select('*')
      .limit(10);
    
    if (relationshipError) {
      console.error('Error accessing medical_event_symptoms table:', relationshipError.message);
      console.error('This may indicate a permissions issue or that the table does not exist.');
      return;
    }
    
    console.log(`Found ${relationshipCheck?.length || 0} records in medical_event_symptoms table`);
    if (relationshipCheck && relationshipCheck.length > 0) {
      console.log('Sample record:', JSON.stringify(relationshipCheck[0], null, 2));
    }

  } catch (error) {
    if (error instanceof Error) {
      console.error('Error linking symptoms to events:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  } finally {
    rl.close();
  }
}

// Function to test direct insertion into the relationship table
async function testDirectInsertion() {
  console.log('Attempting direct insertion into medical_event_symptoms table...');
  
  // First, get a valid medical_event_id
  const { data: events, error: eventsError } = await supabase
    .from('medical_events')
    .select('id')
    .limit(1);
  
  if (eventsError || !events || events.length === 0) {
    console.error('Error fetching a medical event:', eventsError?.message || 'No events found');
    return;
  }
  
  // Then, get a valid symptom_id
  const { data: symptoms, error: symptomsError } = await supabase
    .from('symptoms')
    .select('id')
    .limit(1);
  
  if (symptomsError || !symptoms || symptoms.length === 0) {
    console.error('Error fetching a symptom:', symptomsError?.message || 'No symptoms found');
    return;
  }
  
  const medical_event_id = events[0].id;
  const symptom_id = symptoms[0].id;
  
  console.log(`Testing with medical_event_id: ${medical_event_id}, symptom_id: ${symptom_id}`);
  
  // Attempt to insert a record
  const { data: insertResult, error: insertError } = await supabase
    .from('medical_event_symptoms')
    .insert({
      medical_event_id,
      symptom_id,
      severity: 'moderate', // Example severity
      created_at: new Date().toISOString()
    })
    .select();
  
  if (insertError) {
    console.error('Error inserting relationship:', insertError.message);
    console.error('Details:', JSON.stringify(insertError, null, 2));
    return;
  }
  
  console.log('Successfully inserted relationship:', insertResult);
}

// Main function
const run = async () => {
  try {
    // Test direct insertion
    await testDirectInsertion();
    
    // Check if the medical_event_symptoms table exists and has records
    await linkSymptomsToEvents();

  } catch (error) {
    if (error instanceof Error) {
      console.error('Error linking symptoms to events:', error.message);
    } else {
      console.error('Unknown error:', error);
    }
  } finally {
    console.log('\nProcess completed.');
  }
};

// Run the function
run().catch(console.error); 