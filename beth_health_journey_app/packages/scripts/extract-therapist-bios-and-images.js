require('dotenv').config();
const { Client } = require('@notionhq/client');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

// Initialize Notion client
const notion = new Client({ auth: process.env.NOTION_TOKEN });
const databaseId = process.env.THERAPIST_DB_ID;

// Constants
const CHUNK_SIZE = 10;
const DELAY_MS = 1000;

// Helper function to delay execution
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Get therapists from Notion database in chunks
async function getTherapists(startCursor = undefined) {
  try {
    const response = await notion.databases.query({
      database_id: databaseId,
      start_cursor: startCursor,
      page_size: CHUNK_SIZE,
    });

    return {
      results: response.results.map(page => {
        const urlProperty = page.properties.URL?.url || null;
        const bioProperty = page.properties.Bio?.rich_text || [];
        const imageProperty = page.properties.Image?.files[0]?.file?.url || null;
        const nameProperty = page.properties.Name?.title[0]?.plain_text || 'Unknown';
        const officesProperty = page.properties.Offices?.multi_select || [];
        
        return {
          id: page.id,
          name: nameProperty,
          url: urlProperty,
          hasBio: bioProperty.length > 0,
          imageUrl: imageProperty,
          offices: officesProperty.map(office => office.name)
        };
      }),
      next_cursor: response.next_cursor,
      has_more: response.has_more
    };
  } catch (error) {
    console.error('Error fetching therapists:', error.message);
    return { results: [], next_cursor: null, has_more: false };
  }
}

// Helper function to normalize name variations for better matching
function generateNameVariations(name) {
  const normalizedName = name.toLowerCase().replace(/,|\s*lpc\b|\s*lmft\b|\s*phd\b|\s*psyd\b|\s*md\b|\s*lcsw\b/gi, '').trim();
  const nameParts = normalizedName.split(' ');
  
  const variations = [
    normalizedName,
    // First name only
    nameParts[0],
    // Last name only
    nameParts[nameParts.length - 1],
    // Dr. + Last name
    `dr ${nameParts[nameParts.length - 1]}`,
    // First name + Last name
    `${nameParts[0]} ${nameParts[nameParts.length - 1]}`
  ];
  
  return variations.filter((v, i, a) => a.indexOf(v) === i); // Remove duplicates
}

// Extract bio and image from therapist website
async function extractBioAndImage(url, therapistName) {
  try {
    console.log(`Fetching content for ${therapistName} from ${url}`);
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000
    });

    const $ = cheerio.load(response.data);
    const nameVariations = generateNameVariations(therapistName);
    
    // Extract bio using various possible selectors
    let bio = '';
    
    // Website-specific selectors for well-known therapy practice platforms
    const websiteSpecificBioSelectors = {
      'psychologytoday.com': ['.profile-detail', '#about-me', '.statementPar'],
      'therapistaid.com': ['.provider-bio', '.therapist-description'],
      'goodtherapy.org': ['.profile-content', '.therapist-description'],
      'annathamescounseling.com': ['.team-member-bio', '.staff-bio'],
      'thriveapproach.com': ['.team-bio', '.staff-description'],
      'thrivecounselingnc.com': ['.team-container .description', '.team-member p'],
      'reachingresolution.net': ['.bio-wrapper', '.team-member-content'],
      'neuronnection.com': ['.profile-content', '.therapist-detail-wrapper'],
      'mindpath.com': ['.provider-bio-text', '.provider-profile-content'],
      'oceanwellnessnc.com': ['.staff-member-description', '.team-bio']
    };
    
    // Check for website-specific selectors
    for (const domain in websiteSpecificBioSelectors) {
      if (url.includes(domain)) {
        for (const selector of websiteSpecificBioSelectors[domain]) {
          const bioContent = $(selector).text().trim();
          if (bioContent.length > 200) {
            bio = bioContent;
            console.log(`Found bio using website-specific selector: ${selector}`);
            break;
          }
        }
      }
      if (bio) break;
    }
    
    // If no bio found with website-specific selectors, try name-based selectors
    if (!bio) {
      console.log(`Trying name-based bio selectors for ${therapistName}`);
      const nameBioSelectors = [];
      
      // Generate selectors for each name variation
      for (const nameVar of nameVariations) {
        nameBioSelectors.push(
          // Heading based selectors
          `h1:contains("${nameVar}") ~ p`,
          `h2:contains("${nameVar}") ~ p`,
          `h3:contains("${nameVar}") ~ p`,
          `h4:contains("${nameVar}") ~ p`,
          // Div based selectors
          `div:contains("${nameVar}") ~ p`,
          `div:contains("${nameVar}") > p`,
          // Class based with name
          `.bio:contains("${nameVar}")`,
          `.profile:contains("${nameVar}")`,
          `.team-member:contains("${nameVar}") p`,
          `.staff-member:contains("${nameVar}") p`
        );
      }
      
      // Try each name-based selector
      for (const selector of nameBioSelectors) {
        const elements = $(selector);
        if (elements.length > 0) {
          // Get text from multiple paragraphs if needed
          let bioText = '';
          elements.each((i, el) => {
            const text = $(el).text().trim();
            if (text.length > 50) { // Only include substantial paragraphs
              bioText += text + '\n\n';
            }
          });
          
          if (bioText.length > 200) { // Only use if we found significant text
            bio = bioText.trim();
            console.log(`Found bio using name-based selector: ${selector}`);
            break;
          }
        }
      }
    }
    
    // If still no bio, try generic class-based selectors
    if (!bio) {
      console.log(`Trying generic bio selectors`);
      const genericBioSelectors = [
        '.therapist-bio',
        '.bio-content',
        '.staff-bio',
        '.team-member-bio',
        '.about-me',
        '.provider-bio',
        '.counselor-bio',
        '.bio-section',
        '.profile-content',
        '.about-section',
        '.biography',
        '.profile-bio',
        '.team-member-description',
        '.staff-profile-description',
        '.profile-description',
        '.staff-profile',
        'article .content'
      ];
      
      for (const selector of genericBioSelectors) {
        const bioContent = $(selector).text().trim();
        if (bioContent.length > 200) {
          bio = bioContent;
          console.log(`Found bio using generic selector: ${selector}`);
          break;
        }
      }
    }
    
    // Extract image using various possible selectors
    let imageUrl = null;
    
    // Website-specific image selectors
    const websiteSpecificImageSelectors = {
      'psychologytoday.com': ['.profile-image img', '.profile-photo'],
      'therapistaid.com': ['.provider-photo img', '.therapist-image'],
      'goodtherapy.org': ['.profile-photo img', '.therapist-image'],
      'annathamescounseling.com': ['.team-member-photo img', '.staff-headshot'],
      'thriveapproach.com': ['.team-photo img', '.staff-photo'],
      'thrivecounselingnc.com': ['.team-container img', '.team-member img'],
      'reachingresolution.net': ['.bio-img', '.team-member-photo'],
      'neuronnection.com': ['.profile-image', '.therapist-photo'],
      'mindpath.com': ['.provider-image', '.provider-profile-image'],
      'oceanwellnessnc.com': ['.staff-member-photo', '.team-member-image']
    };
    
    // Check for website-specific image selectors
    for (const domain in websiteSpecificImageSelectors) {
      if (url.includes(domain)) {
        for (const selector of websiteSpecificImageSelectors[domain]) {
          const img = $(selector).first();
          if (img.length > 0) {
            let src = img.attr('src');
            if (!src) continue;
            
            // Make URL absolute if it's relative
            if (!src.startsWith('http')) {
              const baseUrl = new URL(url).origin;
              src = new URL(src, baseUrl).href;
            }
            
            imageUrl = src;
            console.log(`Found image using website-specific selector: ${selector}`);
            break;
          }
        }
      }
      if (imageUrl) break;
    }
    
    // If no image found with website-specific selectors, try name-based selectors
    if (!imageUrl) {
      console.log(`Trying name-based image selectors for ${therapistName}`);
      const nameImageSelectors = [];
      
      // Generate selectors for each name variation
      for (const nameVar of nameVariations) {
        nameImageSelectors.push(
          `img[alt*="${nameVar}" i]`,
          `img[title*="${nameVar}" i]`,
          `.profile:contains("${nameVar}") img`,
          `.bio:contains("${nameVar}") img`,
          `.team-member:contains("${nameVar}") img`,
          `.staff-member:contains("${nameVar}") img`,
          `h1:contains("${nameVar}") ~ img`,
          `h2:contains("${nameVar}") ~ img`,
          `h3:contains("${nameVar}") ~ img`,
          `div:contains("${nameVar}") > img`
        );
      }
      
      // Try each name-based selector
      for (const selector of nameImageSelectors) {
        const img = $(selector).first();
        if (img.length > 0) {
          let src = img.attr('src');
          if (!src) continue;
          
          // Make URL absolute if it's relative
          if (!src.startsWith('http')) {
            const baseUrl = new URL(url).origin;
            src = new URL(src, baseUrl).href;
          }
          
          // Skip likely logo images
          const isLikelyLogo = src.toLowerCase().includes('logo') || 
                              src.toLowerCase().includes('icon') || 
                              src.toLowerCase().includes('header') || 
                              src.toLowerCase().includes('footer') ||
                              src.toLowerCase().includes('banner');
          
          if (!isLikelyLogo) {
            imageUrl = src;
            console.log(`Found image using name-based selector: ${selector}`);
            break;
          }
        }
      }
    }
    
    // If still no image, try generic class-based selectors with image size filtering
    if (!imageUrl) {
      console.log(`Trying generic image selectors`);
      const genericImageSelectors = [
        '.profile-picture img',
        '.profile-photo img',
        '.therapist-photo img',
        '.team-member-photo img',
        '.provider-photo img',
        '.staff-photo img',
        '.profile-image img',
        '.bio-image img',
        '.headshot img',
        '.profile-headshot img',
        '.staff-headshot img',
        '.team-headshot img',
        '.team-photo img'
      ];
      
      for (const selector of genericImageSelectors) {
        const img = $(selector).first();
        if (img.length > 0) {
          let src = img.attr('src');
          if (!src) continue;
          
          // Make URL absolute if it's relative
          if (!src.startsWith('http')) {
            const baseUrl = new URL(url).origin;
            src = new URL(src, baseUrl).href;
          }
          
          // Skip likely logo images or small icons
          const imgWidth = img.attr('width');
          const imgHeight = img.attr('height');
          const isSmallImage = imgWidth && imgHeight && (parseInt(imgWidth) < 100 || parseInt(imgHeight) < 100);
          const isLikelyLogo = src.toLowerCase().includes('logo') || 
                              src.toLowerCase().includes('icon') || 
                              src.toLowerCase().includes('header') || 
                              src.toLowerCase().includes('footer') ||
                              src.toLowerCase().includes('banner') ||
                              isSmallImage;
          
          if (!isLikelyLogo) {
            imageUrl = src;
            console.log(`Found image using generic selector: ${selector}`);
            break;
          }
        }
      }
    }
    
    // Additional check for common image file naming patterns
    if (!imageUrl) {
      const allImages = $('img');
      for (const nameVar of nameVariations) {
        allImages.each((i, img) => {
          if (imageUrl) return false; // Break if image already found
          
          const src = $(img).attr('src');
          if (!src) return true; // Continue to next image
          
          // Check if image filename contains name (common pattern for staff photos)
          const filename = src.split('/').pop().toLowerCase();
          if (filename.includes(nameVar)) {
            // Make URL absolute if it's relative
            if (!src.startsWith('http')) {
              const baseUrl = new URL(url).origin;
              imageUrl = new URL(src, baseUrl).href;
            } else {
              imageUrl = src;
            }
            console.log(`Found image using filename match: ${filename}`);
            return false; // Break the loop
          }
          
          return true; // Continue to next image
        });
        
        if (imageUrl) break;
      }
    }
    
    return { bio, imageUrl };
  } catch (error) {
    console.error(`Error extracting content for ${therapistName}:`, error.message);
    return { bio: '', imageUrl: null };
  }
}

// Update therapist in Notion database
async function updateTherapist(id, bio, imageUrl) {
  try {
    const properties = {};
    let updated = false;
    
    // Only update bio if we found something and it's not empty
    if (bio) {
      // Limit bio length to 2000 characters to avoid hitting Notion API limits
      const truncatedBio = bio.length > 2000 ? bio.substring(0, 1997) + '...' : bio;
      
      properties.Bio = {
        rich_text: [{
          type: "text",
          text: { content: truncatedBio }
        }]
      };
      updated = true;
    }
    
    // Only update image if we found one
    if (imageUrl) {
      properties.Image = {
        files: [{
          name: `profile_image_${Date.now()}.jpg`,
          type: "external",
          external: { url: imageUrl }
        }]
      };
      updated = true;
    }
    
    // Only call the API if we have updates
    if (updated) {
      await notion.pages.update({
        page_id: id,
        properties: properties
      });
      return true;
    }
    
    return false;
  } catch (error) {
    console.error(`Error updating therapist:`, error.message);
    return false;
  }
}

// Process a single therapist
async function processTherapist(therapist) {
  // Skip if no URL
  if (!therapist.url) {
    console.log(`Skipping ${therapist.name}: No URL available`);
    return { skipped: true };
  }
  
  // Extract bio and image
  const { bio, imageUrl } = await extractBioAndImage(therapist.url, therapist.name);
  
  // Determine what needs updating
  const needsBioUpdate = bio && !therapist.hasBio;
  const needsImageUpdate = imageUrl && (!therapist.imageUrl || therapist.imageUrl.includes('logo'));
  
  // Update if needed
  if (needsBioUpdate || needsImageUpdate) {
    const bioToUpdate = needsBioUpdate ? bio : null;
    const imageToUpdate = needsImageUpdate ? imageUrl : null;
    
    console.log(`Updating ${therapist.name}:`);
    if (needsBioUpdate) console.log(`- Adding bio (${bio.length} characters)`);
    if (needsImageUpdate) console.log(`- Adding image: ${imageUrl}`);
    
    const updated = await updateTherapist(
      therapist.id, 
      bioToUpdate, 
      imageToUpdate
    );
    
    if (updated) {
      return {
        updated: true,
        bioUpdated: needsBioUpdate,
        imageUpdated: needsImageUpdate
      };
    }
  } else {
    console.log(`No updates needed for ${therapist.name}`);
  }
  
  return { updated: false };
}

// Main function to process all therapists
async function main() {
  console.log('Starting therapist bio and image extraction process...');
  
  let hasMore = true;
  let startCursor;
  let totalProcessed = 0;
  let totalBiosUpdated = 0;
  let totalImagesUpdated = 0;
  let totalSkipped = 0;
  let totalErrors = 0;
  
  while (hasMore) {
    // Get a chunk of therapists
    const { results, next_cursor, has_more } = await getTherapists(startCursor);
    
    console.log(`Processing chunk of ${results.length} therapists...`);
    
    // Process each therapist in the chunk
    for (const therapist of results) {
      try {
        console.log(`\nProcessing ${therapist.name}...`);
        const result = await processTherapist(therapist);
        
        if (result.skipped) {
          totalSkipped++;
        } else if (result.updated) {
          if (result.bioUpdated) totalBiosUpdated++;
          if (result.imageUpdated) totalImagesUpdated++;
        }
        
        totalProcessed++;
        
        // Add a small delay between therapists to avoid rate limiting
        await delay(DELAY_MS);
      } catch (error) {
        console.error(`Error processing therapist ${therapist.name}:`, error.message);
        totalErrors++;
      }
    }
    
    // Prepare for next chunk
    startCursor = next_cursor;
    hasMore = has_more;
    
    // Add a larger delay between chunks
    if (hasMore) {
      console.log(`\nProcessed ${results.length} therapists. Waiting before processing next chunk...`);
      await delay(DELAY_MS * 3);
    }
  }
  
  // Print summary
  console.log('\n===== SUMMARY =====');
  console.log(`Total therapists processed: ${totalProcessed}`);
  console.log(`Bios updated: ${totalBiosUpdated}`);
  console.log(`Images updated: ${totalImagesUpdated}`);
  console.log(`Therapists skipped (no URL): ${totalSkipped}`);
  console.log(`Errors encountered: ${totalErrors}`);
  console.log('====================');
}

// Run the script
main().catch(error => {
  console.error('An error occurred during execution:', error);
  process.exit(1);
}); 