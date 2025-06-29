import axios, { AxiosError } from 'axios';
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import type { Database } from '../lib/supabase/database.types';

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

const supabase = createClient<Database>(supabaseUrl, supabaseServiceKey);

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * Prompts the user for input
 */
function prompt(question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

/**
 * Main function to extract MyChart data directly using web endpoints
 */
async function extractMyChartData() {
  console.log('===== MyChart Direct Data Extractor =====');
  console.log('This script attempts to extract data directly from MyChart web endpoints.\n');
  
  console.log('INSTRUCTIONS:');
  console.log('1. Log in to your MyChart account in your browser');
  console.log('2. Open browser developer tools (F12 or right-click > Inspect)');
  console.log('3. Go to Application tab > Storage > Local Storage');
  console.log('4. Find "MYCHART-WEB-DEVICE-/myatriumhealth/"');
  console.log('5. Copy the entire value (starts with "WEB,...")\n');
  
  const sessionToken = await prompt('Paste the MyChart localStorage value: ');
  
  if (!sessionToken || !sessionToken.startsWith('WEB,')) {
    console.error('Invalid token format. The token should start with "WEB,"');
    process.exit(1);
  }
  
  // Extract the components of the session token
  const tokenParts = sessionToken.split(',');
  if (tokenParts.length < 3) {
    console.error('Invalid token format. Expected at least 3 parts separated by commas.');
    process.exit(1);
  }
  
  const sessionId = tokenParts[2];
  
  // Create API client for MyChart
  const myChartClient = axios.create({
    baseURL: 'https://my.atriumhealth.org',
    headers: {
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      'X-MyChart-Session': sessionToken,
      'Content-Type': 'application/json'
    },
    withCredentials: true
  });
  
  console.log('\nAttempting to fetch data from MyChart...');
  
  const stats = {
    appointments: { fetched: 0, imported: 0 },
    labResults: { fetched: 0, imported: 0 },
    conditions: { fetched: 0, imported: 0 },
    medications: { fetched: 0, imported: 0 }
  };
  
  try {
    // Try different MyChart endpoints that might work
    
    // 1. Try to get user info/patient ID
    console.log('\nFetching patient information...');
    try {
      const userResponse = await myChartClient.get('/MyChart/Authentication/GetUserInfo');
      console.log('User info found!');
      console.log(JSON.stringify(userResponse.data, null, 2));
      
      // Extract patient ID if available
      if (userResponse.data && userResponse.data.PatientID) {
        console.log(`Patient ID found: ${userResponse.data.PatientID}`);
      }
    } catch (error: any) {
      console.log('Could not retrieve user info:', error.message || 'Unknown error');
    }
    
    // 2. Appointments
    console.log('\nFetching appointments...');
    try {
      // Try multiple possible appointment endpoints
      const appointmentEndpoints = [
        '/MyChart/OpenScheduling/OpenSchedulingAppointments',
        '/MyChart/Appointments/AppointmentList',
        '/MyChart/GetAppointmentInformation'
      ];
      
      let appointmentsFound = false;
      
      for (const endpoint of appointmentEndpoints) {
        try {
          const appointmentsResponse = await myChartClient.get(endpoint);
          if (appointmentsResponse.data) {
            console.log(`Found appointments at endpoint: ${endpoint}`);
            console.log(JSON.stringify(appointmentsResponse.data, null, 2));
            stats.appointments.fetched = Array.isArray(appointmentsResponse.data) 
              ? appointmentsResponse.data.length 
              : 1;
            appointmentsFound = true;
            break;
          }
        } catch (endpointError: any) {
          console.log(`Endpoint ${endpoint} failed: ${endpointError.message || 'Unknown error'}`);
        }
      }
      
      if (!appointmentsFound) {
        console.log('Could not find appointments with any known endpoint.');
      }
    } catch (error: any) {
      console.log('Error fetching appointments:', error.message || 'Unknown error');
    }
    
    // 3. Lab Results
    console.log('\nFetching lab results...');
    try {
      const labEndpoints = [
        '/MyChart/ClinicalInformation/LabResultList',
        '/MyChart/LabResultList',
        '/MyChart/Results/TestList'
      ];
      
      let labsFound = false;
      
      for (const endpoint of labEndpoints) {
        try {
          const labsResponse = await myChartClient.get(endpoint);
          if (labsResponse.data) {
            console.log(`Found lab results at endpoint: ${endpoint}`);
            console.log(JSON.stringify(labsResponse.data, null, 2));
            stats.labResults.fetched = Array.isArray(labsResponse.data) 
              ? labsResponse.data.length 
              : 1;
            labsFound = true;
            break;
          }
        } catch (endpointError: any) {
          console.log(`Endpoint ${endpoint} failed: ${endpointError.message || 'Unknown error'}`);
        }
      }
      
      if (!labsFound) {
        console.log('Could not find lab results with any known endpoint.');
      }
    } catch (error: any) {
      console.log('Error fetching lab results:', error.message || 'Unknown error');
    }
    
    // 4. Medical Conditions
    console.log('\nFetching medical conditions...');
    try {
      const conditionEndpoints = [
        '/MyChart/ClinicalInformation/MedicalConditions',
        '/MyChart/MedicalConditions',
        '/MyChart/Clinical/MedicalConditionList'
      ];
      
      let conditionsFound = false;
      
      for (const endpoint of conditionEndpoints) {
        try {
          const conditionsResponse = await myChartClient.get(endpoint);
          if (conditionsResponse.data) {
            console.log(`Found medical conditions at endpoint: ${endpoint}`);
            console.log(JSON.stringify(conditionsResponse.data, null, 2));
            stats.conditions.fetched = Array.isArray(conditionsResponse.data) 
              ? conditionsResponse.data.length 
              : 1;
            conditionsFound = true;
            break;
          }
        } catch (endpointError: any) {
          console.log(`Endpoint ${endpoint} failed: ${endpointError.message || 'Unknown error'}`);
        }
      }
      
      if (!conditionsFound) {
        console.log('Could not find medical conditions with any known endpoint.');
      }
    } catch (error: any) {
      console.log('Error fetching medical conditions:', error.message || 'Unknown error');
    }
    
    // 5. Medications
    console.log('\nFetching medications...');
    try {
      const medicationEndpoints = [
        '/MyChart/ClinicalInformation/MedicationList',
        '/MyChart/MedicationList',
        '/MyChart/Clinical/MedicationList'
      ];
      
      let medicationsFound = false;
      
      for (const endpoint of medicationEndpoints) {
        try {
          const medicationsResponse = await myChartClient.get(endpoint);
          if (medicationsResponse.data) {
            console.log(`Found medications at endpoint: ${endpoint}`);
            console.log(JSON.stringify(medicationsResponse.data, null, 2));
            stats.medications.fetched = Array.isArray(medicationsResponse.data) 
              ? medicationsResponse.data.length 
              : 1;
            medicationsFound = true;
            break;
          }
        } catch (endpointError: any) {
          console.log(`Endpoint ${endpoint} failed: ${endpointError.message || 'Unknown error'}`);
        }
      }
      
      if (!medicationsFound) {
        console.log('Could not find medications with any known endpoint.');
      }
    } catch (error: any) {
      console.log('Error fetching medications:', error.message || 'Unknown error');
    }
    
    // Summary
    console.log('\n===== EXTRACTION SUMMARY =====');
    console.log(`Appointments: ${stats.appointments.fetched} found`);
    console.log(`Lab Results: ${stats.labResults.fetched} found`);
    console.log(`Conditions: ${stats.conditions.fetched} found`);
    console.log(`Medications: ${stats.medications.fetched} found`);
    
    // Future enhancements: Add import to Supabase functionality
    
  } catch (error: any) {
    console.error('Error during data extraction:', error.message || 'Unknown error');
    if (error.response) {
      console.log('Response status:', error.response.status);
      console.log('Response data:', error.response.data);
    }
  } finally {
    rl.close();
  }
}

// Run the script
extractMyChartData().catch((error: any) => {
  console.error('Unhandled error:', error.message || 'Unknown error');
  rl.close();
  process.exit(1);
}); 