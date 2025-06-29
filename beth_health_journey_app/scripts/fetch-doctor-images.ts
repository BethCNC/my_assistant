import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import axios from 'axios';
import { Client } from '@notionhq/client';
import { createClient } from '@supabase/supabase-js';
import type { Database } from '../lib/supabase/database.types';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string;
const supabase = createClient<Database>(supabaseUrl, supabaseServiceKey);

// Helper function to safely extract values from Notion properties
function getPropertyValue(property: any): any {
  if (!property) return null;
  
  try {
    // Handle different property types
    switch(property.type) {
      case 'title':
        return property.title?.[0]?.plain_text || null;
      case 'rich_text':
        return property.rich_text?.[0]?.plain_text || null;
      case 'select':
        return property.select?.name || null;
      case 'multi_select':
        return property.multi_select?.map((item: any) => item.name) || [];
      case 'phone_number':
        return property.phone_number || null;
      case 'email':
        return property.email || null;
      case 'url':
        return property.url || null;
      case 'date':
        return property.date?.start || null;
      case 'checkbox':
        return property.checkbox || null;
      case 'number':
        return property.number || null;
      default:
        return null;
    }
  } catch (error) {
    console.error(`Error extracting property value:`, error);
    return null;
  }
}

// Function to check if a custom image exists for a doctor
function checkForCustomImage(doctorName: string): string | null {
  const sanitizedName = doctorName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
  const customImagePath = path.join(process.cwd(), 'public', 'doctor-images', 'custom', `${sanitizedName}.jpg`);
  
  if (fs.existsSync(customImagePath)) {
    console.log(`Found custom image for ${doctorName}`);
    return `/doctor-images/custom/${sanitizedName}.jpg`;
  }
  
  return null;
}

// Define the search function
async function searchForDoctorImage(doctorName: string, specialty: string, facilityName?: string, location?: string, useAlternateSearch: boolean = false): Promise<string | null> {
  // First check if we have a custom image
  const customImage = checkForCustomImage(doctorName);
  if (customImage) {
    return customImage;
  }
  
  try {
    console.log(`Searching for image of Dr. ${doctorName} on healthcare websites...`);
    
    // Use the Google Custom Search API with environment variables
    const apiKey = process.env.GOOGLE_API_KEY;
    const searchEngineId = process.env.SEARCH_ENGINE_ID || '20e57adc863c142ff';
    
    if (!apiKey) {
      console.error('Google API key not found in environment variables');
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(doctorName)}&background=random&size=200`;
    }
    
    // Target specific healthcare provider websites
    let query = `${doctorName} doctor`;
    
    // Add specialty if available
    if (specialty) {
      query += ` ${specialty}`;
    }
    
    // Focus on healthcare provider websites
    query += ` site:novanthealth.org OR site:atriumhealth.org OR site:wakehealth.edu OR site:carolinashealthcare.org OR site:wakemedphysicians.com`;
    
    console.log(`Healthcare website search query: ${query}`);
    
    // Call the Google Custom Search API
    const response = await axios.get('https://www.googleapis.com/customsearch/v1', {
      params: {
        key: apiKey,
        cx: searchEngineId,
        q: query,
        searchType: 'image',
        num: 1,
        imgSize: 'medium',
        safe: 'active'
      }
    });
    
    // Extract image URL from the results
    if (response.data.items && response.data.items.length > 0) {
      const imageUrl = response.data.items[0].link;
      
      // Skip x-raw-image URLs
      if (imageUrl.startsWith('x-raw-image://')) {
        console.log(`Found image with unsupported protocol, using placeholder`);
        return `https://ui-avatars.com/api/?name=${encodeURIComponent(doctorName)}&background=random&size=200`;
      }
      
      console.log(`Found official healthcare profile image for ${doctorName}`);
      return imageUrl;
    }
    
    // If no results from healthcare sites, try a more general search
    console.log(`No healthcare profile images found for ${doctorName}, trying general search...`);
    
    const generalResponse = await axios.get('https://www.googleapis.com/customsearch/v1', {
      params: {
        key: apiKey,
        cx: searchEngineId,
        q: `${doctorName} doctor physician ${specialty || ''} ${location || 'North Carolina'}`,
        searchType: 'image',
        num: 1,
        imgSize: 'medium',
        safe: 'active'
      }
    });
    
    if (generalResponse.data.items && generalResponse.data.items.length > 0) {
      const imageUrl = generalResponse.data.items[0].link;
      
      // Skip x-raw-image URLs
      if (!imageUrl.startsWith('x-raw-image://')) {
        console.log(`Found general image for ${doctorName}`);
        return imageUrl;
      }
    }
    
    console.log(`No valid images found for ${doctorName}, using placeholder...`);
  } catch (error) {
    console.error(`Error searching for doctor image:`, error);
  }
  
  // Fall back to placeholder
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(doctorName)}&background=random&size=200`;
}

// Function to download an image
async function downloadImage(url: string, filepath: string): Promise<boolean> {
  try {
    // Skip x-raw-image URLs which aren't supported by axios
    if (url.startsWith('x-raw-image://')) {
      console.error(`Skipping unsupported protocol in URL: ${url}`);
      return false;
    }
    
    // Create the directory if it doesn't exist
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    const response = await axios({
      url,
      method: 'GET',
      responseType: 'stream'
    });
    
    const writer = fs.createWriteStream(filepath);
    
    return new Promise((resolve, reject) => {
      response.data.pipe(writer);
      let error: Error | null = null;
      writer.on('error', err => {
        error = err;
        writer.close();
        reject(err);
      });
      writer.on('close', () => {
        if (!error) {
          console.log(`Image saved to ${filepath}`);
          resolve(true);
        }
      });
    });
  } catch (error) {
    console.error(`Error downloading image:`, error);
    return false;
  }
}

// Function to update Supabase with image paths
async function updateProviderWithImagePath(providerId: string, imagePath: string): Promise<boolean> {
  try {
    const { data, error } = await supabase
      .from('providers')
      .update({ image_url: imagePath })
      .eq('id', providerId);
      
    if (error) {
      console.error(`Error updating provider with image path:`, error);
      return false;
    }
    
    console.log(`Updated provider ${providerId} with image path ${imagePath}`);
    return true;
  } catch (error) {
    console.error(`Error updating provider:`, error);
    return false;
  }
}

// Main function to process all doctors
async function fetchDoctorImages() {
  try {
    console.log('Starting to fetch doctor images...');
    
    // Step 1: Get all providers from Supabase
    console.log('Fetching providers from Supabase...');
    const { data: providers, error } = await supabase
      .from('providers')
      .select('*');
      
    if (error) {
      throw new Error(`Error fetching providers: ${error.message}`);
    }
    
    if (!providers || providers.length === 0) {
      console.log('No providers found in the database.');
      return;
    }
    
    console.log(`Found ${providers.length} providers.`);
    
    // Step 2: For each provider, search for an image and download it
    for (const provider of providers) {
      console.log(`Processing provider: ${provider.name}`);
      
      // Search for the image
      const imageUrl = await searchForDoctorImage(
        provider.name, 
        provider.specialty || 'doctor',
        provider.facility || null,
        provider.location || null
      );
      
      if (!imageUrl) {
        console.log(`No image found for ${provider.name}`);
        continue;
      }
      
      // Create a filename based on the provider's name
      const sanitizedName = provider.name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const filename = `${sanitizedName}.jpg`;
      const imagePath = path.join(process.cwd(), 'public', 'doctor-images', filename);
      const relativeImagePath = `/doctor-images/${filename}`;
      
      // Download the image
      const downloaded = await downloadImage(imageUrl, imagePath);
      
      if (downloaded) {
        // Update the provider record with the image path
        await updateProviderWithImagePath(provider.id, relativeImagePath);
      }
    }
    
    console.log('Doctor image fetch process complete!');
  } catch (error) {
    console.error('Error in fetchDoctorImages:', error);
  }
}

// Alternative function if Notion database is available
async function fetchDoctorImagesFromNotion(databaseId: string) {
  try {
    console.log(`Fetching doctor data from Notion database ${databaseId}...`);
    
    // Query the Notion database with more information
    const response = await notion.databases.query({
      database_id: databaseId,
      page_size: 100, // Increase page size to get all doctors
      filter: {
        // Only process pages with a Name property that's not empty
        property: "Name",
        title: {
          is_not_empty: true
        }
      },
      sorts: [
        // Sort by Name to process in a consistent order
        {
          property: "Name",
          direction: "ascending"
        }
      ]
    });
    
    if (!response.results || response.results.length === 0) {
      console.log('No doctors found in the Notion database.');
      return;
    }
    
    console.log(`Found ${response.results.length} doctors in Notion.`);
    
    // Create the directory if it doesn't exist
    const imagesDir = path.join(process.cwd(), 'public', 'doctor-images');
    if (!fs.existsSync(imagesDir)) {
      fs.mkdirSync(imagesDir, { recursive: true });
    }
    
    // Process each doctor
    const total = response.results.length;
    let processed = 0;
    
    // Log all properties of the first doctor for debugging
    if (response.results.length > 0) {
      const firstDoctor = response.results[0] as any;
      console.log("Available properties in Notion database:");
      if (firstDoctor.properties) {
        Object.keys(firstDoctor.properties).forEach(key => {
          console.log(`- ${key} (${firstDoctor.properties[key].type})`);
        });
      }
    }
    
    for (const page of response.results) {
      // Cast the page to any to access properties safely
      const pageData = page as any;
      
      if (!pageData.properties) {
        console.log('Page properties not found, skipping...');
        processed++;
        console.log(`Progress: ${processed}/${total} (${Math.round(processed/total*100)}%)`);
        continue;
      }
      
      // Extract doctor information
      const name = getPropertyValue(pageData.properties.Name);
      const specialty = getPropertyValue(pageData.properties.Specialty);
      const facility = getPropertyValue(pageData.properties.Facility);
      
      // Try to get location info from different possible property names
      let location = getPropertyValue(pageData.properties.Location) || 
                     getPropertyValue(pageData.properties.Address) || 
                     getPropertyValue(pageData.properties.City) || 
                     getPropertyValue(pageData.properties.Area) || 
                     null;
      
      console.log(`\nProcessing doctor (${processed+1}/${total}): ${name}, ${specialty}`);
      console.log(`Facility: ${facility || 'Unknown'}, Location: ${location || 'Unknown'}`);
      
      if (!name) {
        console.log('Doctor name not found, skipping...');
        processed++;
        console.log(`Progress: ${processed}/${total} (${Math.round(processed/total*100)}%)`);
        continue;
      }
      
      // Search for the image
      const imageUrl = await searchForDoctorImage(name, specialty || 'doctor', facility, location);
      
      if (!imageUrl) {
        console.log(`No image found for ${name}`);
        processed++;
        console.log(`Progress: ${processed}/${total} (${Math.round(processed/total*100)}%)`);
        continue;
      }
      
      // Create a filename based on the doctor's name
      const sanitizedName = name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const filename = `${sanitizedName}.jpg`;
      const imagePath = path.join(imagesDir, filename);
      
      // Download the image
      await downloadImage(imageUrl, imagePath);
      
      processed++;
      console.log(`Processed doctor: ${name}`);
      console.log(`Progress: ${processed}/${total} (${Math.round(processed/total*100)}%)`);
      
      // Add a small delay to avoid overwhelming the system
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    console.log('\nDoctor image fetch process from Notion complete!');
  } catch (error) {
    console.error('Error in fetchDoctorImagesFromNotion:', error);
  }
}

// Determine which function to run based on available database ID
async function main() {
  const notionMedicalTeamDbId = process.env.NOTION_MEDICAL_TEAM_DATABASE_ID;
  
  if (notionMedicalTeamDbId) {
    console.log('Using Notion database for doctor images...');
    await fetchDoctorImagesFromNotion(notionMedicalTeamDbId);
  } else {
    console.log('Notion database ID not found, using Supabase...');
    await fetchDoctorImages();
  }
}

// Run the script
console.log('\n🔍 DOCTOR IMAGE FETCHER 🔍');
console.log('=============================');
console.log('This script will search for and download images of doctors from your medical team.');
console.log('Images will be saved to public/doctor-images/\n');

main()
  .then(() => {
    console.log('\n✅ Doctor image fetch process complete!');
    console.log('Images are stored in the public/doctor-images/ directory');
    console.log('And can be accessed in your app via /doctor-images/{filename}\n');
  })
  .catch(error => {
    console.error('\n❌ Error running doctor image fetcher:', error);
    process.exit(1);
  }); 