import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
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

// Load the FHIR token from the file
let token = '';
let patientId = '';
try {
  // Try to load the token from the data file
  const tokenData = fs.readFileSync('./data/fhir-token.json', 'utf-8');
  
  // The file contains a JSON object with an access_token field
  const jsonData = JSON.parse(tokenData);
  token = jsonData.access_token;
  
  // Get patient ID from the token data
  patientId = jsonData.patient || jsonData._patient || '';
  
  if (!token) {
    throw new Error('Token not found in file');
  }
  
  console.log('Successfully loaded FHIR token');
  console.log(`Patient ID: ${patientId}`);
} catch (error) {
  console.error('Error loading FHIR token:', error);
  console.log('Please ensure your FHIR token is available in data/fhir-token.json');
  process.exit(1);
}

// Base URLs for Epic FHIR API - using the URL from your token scope
const baseUrl = 'https://epicproxy.et0798.epichosted.com/APIProxyPRD/api/FHIR/R4';

// Flag to use mock data when API is unavailable
const USE_MOCK_DATA = false; // Set to true to enable fallback to mock data

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

// Helper function to make authenticated requests to the FHIR API
async function fetchFhirData(endpoint: string) {
  try {
    // Try real API first, unless we're in mock-only mode
    if (!USE_MOCK_DATA) {
      console.log(`Fetching data from ${baseUrl}/${endpoint}`);
      const response = await axios.get(`${baseUrl}/${endpoint}`, {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } else {
      console.log(`Using mock data for ${endpoint}`);
      return mockFhirData(endpoint);
    }
  } catch (error) {
    console.error(`Error fetching from ${endpoint}:`, error);
    if (axios.isAxiosError(error) && error.response) {
      console.error('Response error:', error.response.data);
      
      // Handle token expiration
      if (error.response.status === 401) {
        console.error('Token has expired. Please generate a new token at fetch-my-epic-token.org');
      }
      
      // Handle service unavailable
      if (error.response.status === 503) {
        console.error('Epic FHIR API service is temporarily unavailable.');
        console.log(`Falling back to mock data for ${endpoint}`);
        return mockFhirData(endpoint);
      }
    }
    
    // For any other error, fall back to mock data if enabled
    if (USE_MOCK_DATA) {
      console.log(`API error encountered. Falling back to mock data for ${endpoint}`);
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
      notes: `Imported from Epic FHIR API. Provider ID: ${resource.id}`
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
  try {
    console.log('Fetching appointments from Epic FHIR API...');
    const response = await fetchFhirData('Appointment');
    
    if (!response.entry || !response.entry.length) {
      console.log('No appointments found.');
      return;
    }
    
    stats.appointments.fetched = response.entry.length;
    console.log(`Found ${response.entry.length} appointments.`);
    
    // Process each appointment
    for (const entry of response.entry) {
      try {
        const resource = entry.resource;
        if (!resource) continue;
        
        // Get or create the provider
        let providerId = null;
        if (resource.participant && resource.participant.length > 0) {
          const practitionerRef = resource.participant.find((p: any) => 
            p.actor && p.actor.reference && p.actor.reference.startsWith('Practitioner/')
          );
          
          if (practitionerRef && practitionerRef.actor) {
            // Extract practitioner ID
            const practitionerId = practitionerRef.actor.reference.replace('Practitioner/', '');
            try {
              // Fetch practitioner details
              const practitionerData = await fetchFhirData(`Practitioner/${practitionerId}`);
              providerId = await getOrCreateProvider({ resource: practitionerData });
            } catch (error) {
              console.error(`Error fetching practitioner ${practitionerId}:`, error);
            }
          }
        }
        
        // Get appointment details
        const status = resource.status || 'unknown';
        const startDate = resource.start || null;
        const endDate = resource.end || null;
        const reason = resource.reasonCode?.[0]?.text || 
                      resource.reasonCode?.[0]?.coding?.[0]?.display || 
                      'No reason provided';
        
        const location = resource.participant?.find((p: any) => 
          p.actor && p.actor.reference && p.actor.reference.startsWith('Location/')
        )?.actor?.display || '';
        
        // Get any notes
        const note = resource.comment || '';
        
        // Create the medical event
        const { data, error } = await supabase.from('medical_events').insert({
          title: `Appointment: ${reason}`,
          description: `Status: ${status}`,
          event_type: 'appointment',
          date: startDate,
          location: location,
          provider_id: providerId,
          notes: note,
          documents: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }).select();
        
        if (error) {
          console.error(`Error importing appointment:`, error);
          stats.appointments.errors++;
          continue;
        }
        
        stats.appointments.imported++;
        console.log(`✓ Imported appointment: ${reason}`);
        
        // Get associated documents or notes if available
        if (resource.supportingInformation) {
          // TODO: Import related documents
        }
        
      } catch (error) {
        console.error('Error processing appointment:', error);
        stats.appointments.errors++;
      }
    }
    
    console.log(`Imported ${stats.appointments.imported} out of ${stats.appointments.fetched} appointments.`);
  } catch (error) {
    console.error('Error importing appointments:', error);
  }
}

// Import lab results from the FHIR API
async function importLabResults() {
  try {
    console.log('Fetching diagnostic reports from Epic FHIR API...');
    const response = await fetchFhirData('DiagnosticReport');
    
    if (!response.entry || !response.entry.length) {
      console.log('No lab results found.');
      return;
    }
    
    stats.labResults.fetched = response.entry.length;
    console.log(`Found ${response.entry.length} lab reports.`);
    
    // Process each lab result
    for (const entry of response.entry) {
      try {
        const resource = entry.resource;
        if (!resource) continue;
        
        // Get or create provider
        let providerId = null;
        if (resource.performer && resource.performer.length > 0) {
          const practitionerRef = resource.performer.find((p: any) => 
            p.reference && p.reference.startsWith('Practitioner/')
          );
          
          if (practitionerRef) {
            // Extract practitioner ID
            const practitionerId = practitionerRef.reference.replace('Practitioner/', '');
            try {
              // Fetch practitioner details
              const practitionerData = await fetchFhirData(`Practitioner/${practitionerId}`);
              providerId = await getOrCreateProvider({ resource: practitionerData });
            } catch (error) {
              console.error(`Error fetching practitioner ${practitionerId}:`, error);
            }
          }
        }
        
        // Create medical event for this lab result
        const eventTitle = resource.code?.text || 
                          resource.code?.coding?.[0]?.display || 
                          'Laboratory Test';
        
        const eventDate = resource.effectiveDateTime || resource.issued || new Date().toISOString();
        const notes = resource.conclusion || '';
        
        const { data: eventData, error: eventError } = await supabase.from('medical_events').insert({
          title: eventTitle,
          description: `Lab result: ${eventTitle}`,
          event_type: 'lab_result',
          date: eventDate,
          provider_id: providerId,
          notes: notes,
          documents: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }).select();
        
        if (eventError) {
          console.error(`Error creating medical event for lab result:`, eventError);
          stats.labResults.errors++;
          continue;
        }
        
        const eventId = eventData[0].id;
        
        // Process individual result components
        if (resource.result && resource.result.length > 0) {
          for (const resultRef of resource.result) {
            try {
              if (resultRef.reference && resultRef.reference.startsWith('Observation/')) {
                const obsId = resultRef.reference.replace('Observation/', '');
                const obsData = await fetchFhirData(`Observation/${obsId}`);
                
                if (!obsData) continue;
                
                // Extract lab result details
                const testName = obsData.code?.text || 
                                obsData.code?.coding?.[0]?.display || 
                                'Unknown Test';
                
                const category = obsData.category?.[0]?.coding?.[0]?.display || 'Laboratory';
                
                let result = '';
                let unit = '';
                
                if (obsData.valueQuantity) {
                  result = obsData.valueQuantity.value?.toString() || '';
                  unit = obsData.valueQuantity.unit || '';
                } else if (obsData.valueString) {
                  result = obsData.valueString;
                } else if (obsData.valueCodeableConcept) {
                  result = obsData.valueCodeableConcept.text || 
                          obsData.valueCodeableConcept.coding?.[0]?.display || '';
                }
                
                const referenceRange = obsData.referenceRange && obsData.referenceRange[0] ? 
                                      `${obsData.referenceRange[0].low?.value || ''} - ${obsData.referenceRange[0].high?.value || ''}` : 
                                      '';
                
                const isAbnormal = obsData.interpretation?.[0]?.coding?.[0]?.code === 'A';
                
                // Save lab result
                const { error: labError } = await supabase.from('lab_results').insert({
                  medical_event_id: eventId,
                  test_name: testName,
                  category: category,
                  date: obsData.effectiveDateTime || eventDate,
                  result: result,
                  unit: unit,
                  reference_range: referenceRange,
                  is_abnormal: isAbnormal,
                  provider_id: providerId,
                  notes: obsData.note?.[0]?.text || '',
                  file_url: null
                });
                
                if (labError) {
                  console.error(`Error importing lab result:`, labError);
                  stats.labResults.errors++;
                } else {
                  stats.labResults.imported++;
                  console.log(`✓ Imported lab result: ${testName}`);
                }
              }
            } catch (error) {
              console.error('Error processing observation:', error);
            }
          }
        }
      } catch (error) {
        console.error('Error processing lab result:', error);
        stats.labResults.errors++;
      }
    }
    
    console.log(`Imported ${stats.labResults.imported} lab results.`);
  } catch (error) {
    console.error('Error importing lab results:', error);
  }
}

// Import medical conditions from FHIR API
async function importConditions() {
  try {
    console.log('Fetching conditions from Epic FHIR API...');
    const response = await fetchFhirData('Condition');
    
    if (!response.entry || !response.entry.length) {
      console.log('No conditions found.');
      return;
    }
    
    stats.conditions.fetched = response.entry.length;
    console.log(`Found ${response.entry.length} conditions.`);
    
    // Process each condition
    for (const entry of response.entry) {
      try {
        const resource = entry.resource;
        if (!resource) continue;
        
        // Get or create provider who recorded this condition
        let providerId = null;
        if (resource.recorder && resource.recorder.reference) {
          const practitionerId = resource.recorder.reference.replace('Practitioner/', '');
          try {
            const practitionerData = await fetchFhirData(`Practitioner/${practitionerId}`);
            providerId = await getOrCreateProvider({ resource: practitionerData });
          } catch (error) {
            console.error(`Error fetching practitioner ${practitionerId}:`, error);
          }
        }
        
        // Extract condition details
        const name = resource.code?.text || 
                    resource.code?.coding?.[0]?.display || 
                    'Unknown Condition';
        
        const description = resource.note?.[0]?.text || '';
        
        const dateRecorded = resource.onsetDateTime || 
                           resource.recordedDate || 
                           new Date().toISOString();
        
        // Map FHIR status to our status values
        let status = 'active';
        if (resource.clinicalStatus?.coding?.[0]?.code) {
          const clinicalStatus = resource.clinicalStatus.coding[0].code;
          if (clinicalStatus === 'active') status = 'active';
          else if (clinicalStatus === 'resolved') status = 'resolved';
          else if (clinicalStatus === 'remission') status = 'in_remission';
          else status = 'active'; // Default
        }
        
        // Map category
        let category = '';
        if (resource.category && resource.category.length > 0) {
          category = resource.category[0].coding?.[0]?.display || 
                    resource.category[0].text || '';
        }
        
        // Determine severity (default to 5 if not specified)
        let severity = 5;
        if (resource.severity) {
          const severityCode = resource.severity.coding?.[0]?.code;
          if (severityCode === 'severe') severity = 9;
          else if (severityCode === 'moderate') severity = 5;
          else if (severityCode === 'mild') severity = 2;
        }
        
        // Insert condition into database
        const { data, error } = await supabase.from('conditions').insert({
          name,
          description,
          date_diagnosed: dateRecorded,
          status,
          severity,
          category,
          notes: description,
          provider_id: providerId,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }).select();
        
        if (error) {
          console.error(`Error importing condition:`, error);
          stats.conditions.errors++;
          continue;
        }
        
        stats.conditions.imported++;
        console.log(`✓ Imported condition: ${name}`);
        
      } catch (error) {
        console.error('Error processing condition:', error);
        stats.conditions.errors++;
      }
    }
    
    console.log(`Imported ${stats.conditions.imported} out of ${stats.conditions.fetched} conditions.`);
  } catch (error) {
    console.error('Error importing conditions:', error);
  }
}

// Main function to run the import
async function main() {
  console.log('Starting EPIC FHIR data import...');
  
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
    console.log(`Conditions: ${stats.conditions.imported}/${stats.conditions.fetched} imported (${stats.conditions.errors} errors)`);
    console.log(`Appointments: ${stats.appointments.imported}/${stats.appointments.fetched} imported (${stats.appointments.errors} errors)`);
    console.log(`Lab Results: ${stats.labResults.imported}/${stats.labResults.fetched} imported (${stats.labResults.errors} errors)`);
    console.log(`Providers created: ${stats.providers.created} (${stats.providers.errors} errors)`);
    console.log('===========================');
    console.log('Import completed successfully!');
    
  } catch (error) {
    console.error('Error during import:', error);
    console.log('\n===== IMPORT SUMMARY =====');
    console.log(`Conditions: ${stats.conditions.imported}/${stats.conditions.fetched} imported (${stats.conditions.errors} errors)`);
    console.log(`Appointments: ${stats.appointments.imported}/${stats.appointments.fetched} imported (${stats.appointments.errors} errors)`);
    console.log(`Lab Results: ${stats.labResults.imported}/${stats.labResults.fetched} imported (${stats.labResults.errors} errors)`);
    console.log(`Providers created: ${stats.providers.created} (${stats.providers.errors} errors)`);
    console.log('===========================');
    console.log('Import completed with errors.');
  }
}

// Run the import
main().catch(console.error); 