require('dotenv').config();
const { Client } = require('@notionhq/client');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// Initialize Notion client
const notion = new Client({ auth: process.env.NOTION_TOKEN });
const databaseId = process.env.THERAPIST_DB_ID;

async function getExistingTherapists() {
  const response = await notion.databases.query({
    database_id: databaseId,
  });

  return response.results.map(page => {
    const id = page.id;
    const nameProperty = page.properties.Name;
    const name = nameProperty.title.length > 0 ? nameProperty.title[0].plain_text : 'Unknown';
    
    // Use URL property instead of website
    const urlProperty = page.properties.URL;
    const url = urlProperty.url || null;
    
    const imageProperty = page.properties.Image;
    const image = imageProperty.files.length > 0 ? imageProperty.files[0].external?.url : null;
    
    return { id, name, url, image };
  });
}

async function extractImageFromWebsite(url) {
  try {
    console.log(`  Scraping website: ${url}`);
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });
    
    const $ = cheerio.load(response.data);
    let potentialImages = [];
    
    // Common selectors for therapist profile images
    const selectors = [
      // Specific profile image selectors
      'img.profile-image', 'img.therapist-photo', 'img.profile-photo',
      'img.profile-picture', 'img.therapist-image', 'img.team-photo',
      'img.staff-photo', '.staff-profile img', '.therapist-profile img',
      '.about-me img', '.bio img', '.profile img', '.team-member img',
      
      // Look for images in headers and main content
      'header img', 'main img', '.header img', '.main img',
      
      // Fall back to any img tags if needed
      'img'
    ];
    
    // Try each selector in order of specificity
    for (const selector of selectors) {
      $(selector).each((i, el) => {
        const src = $(el).attr('src');
        if (src && !src.includes('logo') && !src.includes('icon') && 
            !potentialImages.includes(src)) {
          potentialImages.push(src);
        }
      });
      
      // If we found specific profile images, stop looking
      if (potentialImages.length > 0 && selector !== 'img') {
        break;
      }
    }
    
    // If we found potential images, choose the first one
    // and resolve relative URLs to absolute ones
    if (potentialImages.length > 0) {
      const imageSrc = potentialImages[0];
      if (imageSrc.startsWith('http')) {
        return imageSrc;
      } else if (imageSrc.startsWith('//')) {
        return `https:${imageSrc}`;
      } else if (imageSrc.startsWith('/')) {
        // Handle relative URLs
        const urlObj = new URL(url);
        const baseUrl = `${urlObj.protocol}//${urlObj.host}`;
        return `${baseUrl}${imageSrc}`;
      } else {
        // Handle relative URLs without leading slash
        const urlObj = new URL(url);
        const baseUrl = `${urlObj.protocol}//${urlObj.host}${urlObj.pathname}`;
        if (baseUrl.endsWith('/')) {
          return `${baseUrl}${imageSrc}`;
        } else {
          // Remove the file part from the pathname
          const basePath = baseUrl.split('/').slice(0, -1).join('/');
          return `${basePath}/${imageSrc}`;
        }
      }
    }
    
    return null;
  } catch (error) {
    console.error(`  Error scraping website: ${error.message}`);
    return null;
  }
}

async function updateTherapistWithImage(therapistId, imageUrl) {
  try {
    await notion.pages.update({
      page_id: therapistId,
      properties: {
        Image: {
          files: [
            {
              type: 'external',
              name: 'profile_image',
              external: {
                url: imageUrl
              }
            }
          ]
        }
      }
    });
    return true;
  } catch (error) {
    console.error(`  Error updating therapist image: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('Starting image extraction process...');
  
  // Get existing therapists
  const therapists = await getExistingTherapists();
  console.log(`Found ${therapists.length} therapists in database`);
  
  let updated = 0;
  let skipped = 0;
  let errors = 0;
  
  // Process each therapist
  for (const therapist of therapists) {
    console.log(`Processing therapist: ${therapist.name}`);
    
    // Skip if no URL or image already exists
    if (!therapist.url) {
      console.log(`  Skipping: No URL provided`);
      skipped++;
      continue;
    }
    
    if (therapist.image) {
      console.log(`  Skipping: Image already exists`);
      skipped++;
      continue;
    }
    
    // Extract image from website
    const imageUrl = await extractImageFromWebsite(therapist.url);
    
    if (!imageUrl) {
      console.log(`  No suitable image found on website`);
      skipped++;
      continue;
    }
    
    console.log(`  Found image: ${imageUrl}`);
    
    // Update therapist with image
    const success = await updateTherapistWithImage(therapist.id, imageUrl);
    
    if (success) {
      console.log(`  Successfully updated ${therapist.name} with image`);
      updated++;
    } else {
      console.log(`  Failed to update ${therapist.name} with image`);
      errors++;
    }
    
    // Add small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  // Print summary
  console.log('\nImage extraction process completed');
  console.log(`Total therapists processed: ${therapists.length}`);
  console.log(`Therapists updated with images: ${updated}`);
  console.log(`Therapists skipped (no URL or image exists): ${skipped}`);
  console.log(`Errors: ${errors}`);
}

// Run the main function
main()
  .then(() => console.log('Script completed successfully'))
  .catch(error => console.error('Error running script:', error)); 