import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import type { Database } from '../lib/supabase/database.types';

// Parse command line arguments
const args = process.argv.slice(2);
const USE_MOCK_DATA = args.includes('--mock');

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

// Health system selection
const HEALTH_SYSTEM = process.env.HEALTH_SYSTEM || 'novant';
console.log(`Using health system: ${HEALTH_SYSTEM.toUpperCase()}`);

// Set the base URL and token file path based on the health system
let baseUrl = '';
let tokenFilePath = '';
let patientIdKey = 'patient_id';

if (HEALTH_SYSTEM.toLowerCase() === 'novant') {
  baseUrl = 'https://oauth.epic.com/FHIR/api/FHIR/R4';
  tokenFilePath = path.join(process.cwd(), 'data/fhir-token.json');
} else if (HEALTH_SYSTEM.toLowerCase() === 'atrium') {
  // Try multiple possible Atrium endpoints
  baseUrl = 'https://my.atriumhealth.org/FHIR/api/FHIR/R4';
  tokenFilePath = path.join(process.cwd(), 'data/atrium-fhir-token.json');
  patientIdKey = 'patient_id'; // May be different for Atrium
}

// Load the FHIR token from the file
let token = '';
let patientId = '';
let tokenType = 'Bearer';
let isMyChartSession = false;
try {
  // Try to load the token from the data file
  const tokenData = fs.readFileSync(tokenFilePath, 'utf-8');
  
  // The file contains a JSON object with an access_token field
  const jsonData = JSON.parse(tokenData);
  token = jsonData.access_token;
  tokenType = jsonData.token_type || 'Bearer';
  isMyChartSession = jsonData.mychart_session === true;
  
  // Get patient ID from the token data
  patientId = jsonData.patient || jsonData._patient || '';
  
  if (!token) {
    throw new Error('Token not found in file');
  }
  
  console.log(`Successfully loaded ${HEALTH_SYSTEM.toUpperCase()} FHIR token`);
  console.log(`Token type: ${isMyChartSession ? 'MyChart Session' : tokenType}`);
  console.log(`Patient ID: ${patientId || 'Not specified'}`);
} catch (error) {
  console.error(`Error loading ${HEALTH_SYSTEM} FHIR token:`, error);
  console.log(`Please ensure your FHIR token is available in ${tokenFilePath}`);
  process.exit(1);
}

// Track statistics
const stats = {
  appointments: {
    fetched: 0,
    imported: 0,
    errors: 0
  },
  labResults: {
    fetched: 0,
    imported: 0,
    errors: 0
  },
  conditions: {
    fetched: 0,
    imported: 0,
    errors: 0
  },
  providers: {
    created: 0,
    errors: 0
  }
};

// Helper function to fetch data from the FHIR API with the token
async function fetchFhirData(endpoint: string) {
  if (USE_MOCK_DATA) {
    console.log(`Using mock data for ${endpoint}`);
    return mockFhirData(endpoint);
  }
  
  // First attempt with the current baseUrl
  let currentBaseUrl = baseUrl;
  let error = null;
  
  // Try a series of possible URL patterns for Atrium Health
  const possibleUrlPatterns = [
    baseUrl,
    'https://my.atriumhealth.org/FHIR/api/FHIR/R4',
    'https://my.atriumhealth.org/api/FHIR/R4',
    'https://mychart.atriumhealth.org/FHIR/api/FHIR/R4',
    'https://mychart.atriumhealth.org/api/FHIR/R4',
    'https://mychart.atriumhealth.org/MCAPI/api/FHIR/R4',
    'https://mychart.atriumhealth.org/MYCHART/api/FHIR/R4'
  ];
  
  if (HEALTH_SYSTEM.toLowerCase() === 'atrium') {
    console.log(`Testing multiple URL patterns for Atrium Health...`);
    
    for (const testUrl of possibleUrlPatterns) {
      try {
        console.log(`Trying endpoint: ${testUrl}/${endpoint}`);
        
        const headers: Record<string, string> = {
          Accept: 'application/json',
        };
        
        // Add authorization header based on token type
        if (isMyChartSession) {
          // For MyChart session tokens from localStorage
          headers['X-MyChart-Session'] = token;
        } else {
          // Standard OAuth2 bearer token
          headers['Authorization'] = `${tokenType} ${token}`;
        }
        
        // Add patient ID header if available
        if (patientId) {
          if (HEALTH_SYSTEM.toLowerCase() === 'atrium') {
            headers['X-MyChart-PatientID'] = patientId;
          } else {
            headers['X-Epic-Patient-Id'] = patientId;
          }
        }
        
        // Add other common headers that might be needed
        headers['X-Requested-With'] = 'XMLHttpRequest';
        
        const response = await axios.get(`${testUrl}/${endpoint}`, {
          headers,
          withCredentials: true,
          allowAbsoluteUrls: true,
        });
        
        console.log(`SUCCESS with endpoint: ${testUrl}/${endpoint}`);
        // If we get here, the URL worked
        baseUrl = testUrl; // Update the baseUrl for future calls
        return response.data;
      } catch (err: any) {
        console.error(`Error with endpoint ${testUrl}/${endpoint}:`, err.message);
        error = err;
        
        // If we get a different error than 404, this might be the right URL
        if (err.response && err.response.status !== 404) {
          console.log(`Got non-404 response from ${testUrl}/${endpoint}: ${err.response.status}`);
          console.log(`Response headers:`, err.response.headers);
          
          // This could be an authentication error rather than a wrong URL
          if (err.response.status === 401 || err.response.status === 403) {
            console.log(`This might be the correct URL but with an authentication issue`);
            baseUrl = testUrl; // Update the baseUrl for future calls
            throw err; // Re-throw to allow proper handling
          }
        }
      }
    }
  } else {
    // For non-Atrium (e.g., Novant), use the original method
    try {
      const headers: Record<string, string> = {
        Accept: 'application/json',
      };
      
      // Add authorization header
      headers['Authorization'] = `${tokenType} ${token}`;
      
      // Add Epic-specific headers
      if (HEALTH_SYSTEM.toLowerCase() === 'novant') {
        headers['X-Epic-Patient-Id'] = patientId;
      }
      
      const response = await axios.get(`${currentBaseUrl}/${endpoint}`, {
        headers,
        allowAbsoluteUrls: true,
      });
      
      return response.data;
    } catch (err) {
      error = err;
    }
  }

  // If all attempts failed
  if (error) {
    // If it's an Axios error, log more details
    if (error.isAxiosError) {
      console.error(`Error fetching from ${endpoint}:`, error);
      
      if (error.response) {
        console.log('Response status:', error.response.status);
        console.log('Response data:', error.response.data);
        
        // Check for token expiration
        if (error.response.status === 401) {
          console.error('Your token may have expired. Please update your token using the update-fhir-token.ts script.');
        }
      } else if (error.request) {
        console.log('No response received from the server. The service may be unavailable.');
      }
    } else {
      console.error(`Unknown error:`, error);
    }
    
    if (USE_MOCK_DATA) {
      console.log(`Falling back to mock data for ${endpoint}`);
      return mockFhirData(endpoint);
    }
    
    throw error;
  }
}

// Mock data for when the API is unavailable
function mockFhirData(endpoint: string) {
  console.log(`Generating mock data for ${endpoint}`);
  
  // Mock Patient data
  if (endpoint === 'Patient') {
    return {
      resourceType: 'Patient',
      id: 'mock-patient-id',
      name: [{ 
        given: ['Beth'],
        family: 'Cartrette'
      }],
      gender: 'female',
      birthDate: '1982-09-13'
    };
  }
  
  // Mock Condition data
  if (endpoint === 'Condition') {
    return {
      resourceType: 'Bundle',
      type: 'searchset',
      total: 2,
      entry: [
        {
          resource: {
            resourceType: 'Condition',
            id: 'condition-1',
            code: {
              text: 'Migraine'
            },
            recordedDate: '2022-03-15',
            clinicalStatus: {
              coding: [
                {
                  code: 'active'
                }
              ]
            },
            severity: {
              coding: [
                {
                  code: 'moderate'
                }
              ]
            },
            category: [
              {
                coding: [
                  {
                    display: 'Neurological'
                  }
                ]
              }
            ]
          }
        },
        {
          resource: {
            resourceType: 'Condition',
            id: 'condition-2',
            code: {
              text: 'Asthma'
            },
            recordedDate: '2020-05-10',
            clinicalStatus: {
              coding: [
                {
                  code: 'active'
                }
              ]
            },
            severity: {
              coding: [
                {
                  code: 'mild'
                }
              ]
            },
            category: [
              {
                coding: [
                  {
                    display: 'Respiratory'
                  }
                ]
              }
            ]
          }
        }
      ]
    };
  }
  
  // Mock Appointment data
  if (endpoint === 'Appointment') {
    return {
      resourceType: 'Bundle',
      type: 'searchset',
      total: 2,
      entry: [
        {
          resource: {
            resourceType: 'Appointment',
            id: 'appointment-1',
            status: 'booked',
            start: '2023-01-15T09:00:00Z',
            end: '2023-01-15T09:30:00Z',
            reasonCode: [
              {
                text: 'Annual Physical'
              }
            ],
            participant: [
              {
                actor: {
                  reference: 'Practitioner/doctor-1',
                  display: 'Dr. Smith'
                }
              }
            ]
          }
        },
        {
          resource: {
            resourceType: 'Appointment',
            id: 'appointment-2',
            status: 'booked',
            start: '2023-02-20T13:00:00Z',
            end: '2023-02-20T13:45:00Z',
            reasonCode: [
              {
                text: 'Migraine Follow-up'
              }
            ],
            participant: [
              {
                actor: {
                  reference: 'Practitioner/doctor-2',
                  display: 'Dr. Johnson'
                }
              }
            ]
          }
        }
      ]
    };
  }
  
  // Mock DiagnosticReport (lab results) data
  if (endpoint === 'DiagnosticReport') {
    return {
      resourceType: 'Bundle',
      type: 'searchset',
      total: 1,
      entry: [
        {
          resource: {
            resourceType: 'DiagnosticReport',
            id: 'report-1',
            status: 'final',
            code: {
              text: 'Complete Blood Count'
            },
            issued: '2023-03-10T11:45:00Z',
            result: [
              {
                reference: 'Observation/obs-1'
              },
              {
                reference: 'Observation/obs-2'
              }
            ]
          }
        }
      ]
    };
  }
  
  // Mock Observation data
  if (endpoint.startsWith('Observation/')) {
    if (endpoint === 'Observation/obs-1') {
      return {
        resourceType: 'Observation',
        id: 'obs-1',
        status: 'final',
        code: {
          text: 'Hemoglobin'
        },
        valueQuantity: {
          value: 14.2,
          unit: 'g/dL'
        },
        referenceRange: [
          {
            low: {
              value: 12.0
            },
            high: {
              value: 16.0
            }
          }
        ]
      };
    } else {
      return {
        resourceType: 'Observation',
        id: 'obs-2',
        status: 'final',
        code: {
          text: 'White Blood Cell Count'
        },
        valueQuantity: {
          value: 7.5,
          unit: 'x10^9/L'
        },
        referenceRange: [
          {
            low: {
              value: 4.5
            },
            high: {
              value: 11.0
            }
          }
        ]
      };
    }
  }
  
  // Mock Practitioner data
  if (endpoint.startsWith('Practitioner/')) {
    if (endpoint === 'Practitioner/doctor-1') {
      return {
        resourceType: 'Practitioner',
        id: 'doctor-1',
        name: [
          {
            prefix: ['Dr.'],
            given: ['John'],
            family: 'Smith'
          }
        ],
        qualification: [
          {
            code: {
              text: 'Family Medicine'
            }
          }
        ]
      };
    } else {
      return {
        resourceType: 'Practitioner',
        id: 'doctor-2',
        name: [
          {
            prefix: ['Dr.'],
            given: ['Sarah'],
            family: 'Johnson'
          }
        ],
        qualification: [
          {
            code: {
              text: 'Neurology'
            }
          }
        ]
      };
    }
  }
  
  // Default empty response
  return {
    resourceType: 'Bundle',
    type: 'searchset',
    total: 0,
    entry: []
  };
}

// Get or create a provider in the database
async function getOrCreateProvider(practitioner: any): Promise<string | null> {
  if (!practitioner || !practitioner.resource) return null;
  
  const resource = practitioner.resource;
  
  // Extract provider details
  const name = resource.name && resource.name[0] ? 
    [
      resource.name[0].prefix?.join(' ') || '',
      resource.name[0].given?.join(' ') || '',
      resource.name[0].family || ''
    ].filter(Boolean).join(' ').trim() : 
    'Unknown Provider';
  
  // Check if provider already exists
  const { data: existingProviders } = await supabase
    .from('providers')
    .select('*')
    .ilike('name', name)
    .limit(1);
  
  if (existingProviders && existingProviders.length > 0) {
    return existingProviders[0].id;
  }
  
  // Extract specialty
  let specialty = '';
  if (resource.qualification && resource.qualification.length > 0) {
    const qualifications = resource.qualification.map((q: any) => 
      q.code?.text || q.code?.coding?.[0]?.display || ''
    ).filter(Boolean);
    
    specialty = qualifications.join(', ');
  }
  
  // Extract contact details
  let phone = '';
  let email = '';
  let address = '';
  
  if (resource.telecom && resource.telecom.length > 0) {
    const phoneObj = resource.telecom.find((t: any) => t.system === 'phone');
    const emailObj = resource.telecom.find((t: any) => t.system === 'email');
    
    phone = phoneObj?.value || '';
    email = emailObj?.value || '';
  }
  
  if (resource.address && resource.address.length > 0) {
    const addr = resource.address[0];
    address = [
      addr.line?.join(' ') || '',
      addr.city || '',
      addr.state || '',
      addr.postalCode || '',
      addr.country || ''
    ].filter(Boolean).join(', ');
  }
  
  // Create provider
  try {
    const { data, error } = await supabase.from('providers').insert({
      name,
      specialty,
      facility: resource.organization?.display || '',
      address,
      phone,
      email,
      notes: `Imported from ${HEALTH_SYSTEM.toUpperCase()} FHIR API. Provider ID: ${resource.id}`
    }).select();
    
    if (error) {
      console.error('Error creating provider:', error);
      stats.providers.errors++;
      return null;
    }
    
    stats.providers.created++;
    console.log(`Created provider: ${name}`);
    return data[0].id;
  } catch (error) {
    console.error('Error creating provider:', error);
    stats.providers.errors++;
    return null;
  }
}

// Import appointments from the FHIR API
async function importAppointments() {
  // Implementation same as in import-from-epic.ts
  try {
    console.log(`Fetching appointments from ${HEALTH_SYSTEM.toUpperCase()} FHIR API...`);
    const response = await fetchFhirData('Appointment');
    
    if (!response.entry || !response.entry.length) {
      console.log('No appointments found.');
      return;
    }
    
    stats.appointments.fetched = response.entry.length;
    console.log(`Found ${response.entry.length} appointments.`);
    
    // Process each appointment 
    // (rest of implementation would mirror the one in import-from-epic.ts)
    // ...
    
  } catch (error) {
    console.error('Error importing appointments:', error);
  }
}

// Import lab results from the FHIR API
async function importLabResults() {
  // Implementation same as in import-from-epic.ts
  try {
    console.log(`Fetching diagnostic reports from ${HEALTH_SYSTEM.toUpperCase()} FHIR API...`);
    const response = await fetchFhirData('DiagnosticReport');
    
    // Rest of implementation would mirror the one in import-from-epic.ts
    // ...
    
  } catch (error) {
    console.error('Error importing lab results:', error);
  }
}

// Import medical conditions from FHIR API
async function importConditions() {
  // Implementation same as in import-from-epic.ts
  try {
    console.log(`Fetching conditions from ${HEALTH_SYSTEM.toUpperCase()} FHIR API...`);
    const response = await fetchFhirData('Condition');
    
    // Rest of implementation would mirror the one in import-from-epic.ts
    // ...
    
  } catch (error) {
    console.error('Error importing conditions:', error);
  }
}

// Main function to run the import
async function main() {
  console.log(`Starting ${HEALTH_SYSTEM.toUpperCase()} FHIR data import...`);
  
  try {
    // Verify FHIR API access
    console.log('Verifying FHIR API access...');
    const patientData = await fetchFhirData('Patient');
    console.log('Successfully connected to FHIR API');
    
    // Import conditions
    await importConditions();
    
    // Import appointments
    await importAppointments();
    
    // Import lab results
    await importLabResults();
    
    // Print import summary
    console.log('\n===== IMPORT SUMMARY =====');
    console.log(`Health System: ${HEALTH_SYSTEM.toUpperCase()}`);
    console.log(`Conditions: ${stats.conditions.imported}/${stats.conditions.fetched} imported (${stats.conditions.errors} errors)`);
    console.log(`Appointments: ${stats.appointments.imported}/${stats.appointments.fetched} imported (${stats.appointments.errors} errors)`);
    console.log(`Lab Results: ${stats.labResults.imported}/${stats.labResults.fetched} imported (${stats.labResults.errors} errors)`);
    console.log(`Providers created: ${stats.providers.created} (${stats.providers.errors} errors)`);
    console.log('===========================');
    console.log('Import completed successfully!');
    
  } catch (error) {
    console.error('Error during import:', error);
    console.log('\n===== IMPORT SUMMARY =====');
    console.log(`Health System: ${HEALTH_SYSTEM.toUpperCase()}`);
    console.log(`Conditions: ${stats.conditions.imported}/${stats.conditions.fetched} imported (${stats.conditions.errors} errors)`);
    console.log(`Appointments: ${stats.appointments.imported}/${stats.appointments.fetched} imported (${stats.appointments.errors} errors)`);
    console.log(`Lab Results: ${stats.labResults.imported}/${stats.labResults.fetched} imported (${stats.labResults.errors} errors)`);
    console.log(`Providers created: ${stats.providers.created} (${stats.providers.errors} errors)`);
    console.log('===========================');
    console.log('Import completed with errors.');
  }
}

// Run the script
main().catch((error) => {
  console.error('Unhandled error:', error);
  process.exit(1);
}); 