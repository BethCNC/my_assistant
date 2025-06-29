const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

// Constants
const THRIVE_TEAM_URL = 'https://www.thrivecounselingnc.com/team';
const OUTPUT_CSV = path.join(__dirname, '../data/thrive-therapists.csv');
const OUTPUT_JSON = path.join(__dirname, '../data/thrive-therapists.json');
const IMAGE_DIR = path.join(__dirname, '../public/images/therapists');
const DELAY_MS = 1000; // Delay between requests to avoid overwhelming the server

// Helper function to delay execution
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// Ensure directories exist
const dataDir = path.join(__dirname, '../data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

if (!fs.existsSync(IMAGE_DIR)) {
  fs.mkdirSync(IMAGE_DIR, { recursive: true });
}

// Set up CSV writer
const csvWriter = createObjectCsvWriter({
  path: OUTPUT_CSV,
  header: [
    { id: 'name', title: 'Name' },
    { id: 'title', title: 'Title' },
    { id: 'imageUrl', title: 'Image URL' },
    { id: 'localImagePath', title: 'Local Image Path' },
    { id: 'fullBioUrl', title: 'Bio Page URL' },
    { id: 'bio', title: 'Bio' }
  ]
});

/**
 * Fetch HTML content from a URL with error handling and retries
 */
async function fetchUrl(url, retries = 3) {
  try {
    console.log(`Fetching ${url}...`);
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${url}: ${error.message}`);
    if (retries > 0) {
      console.log(`Retrying... (${retries} attempts left)`);
      await delay(2000);
      return fetchUrl(url, retries - 1);
    }
    throw error;
  }
}

/**
 * Extract full bio from therapist detail page
 */
async function extractTherapistBio(url, therapistName) {
  if (!url) {
    console.log(`No URL provided for ${therapistName}, skipping bio extraction`);
    return '';
  }
  
  try {
    console.log(`Fetching bio for ${therapistName} from ${url}`);
    const html = await fetchUrl(url);
    const $ = cheerio.load(html);
    let bioContent = '';
    
    // Try different potential selectors for bio content
    const bioSelectors = [
      '.bio-content, .about-me, .therapist-bio, .provider-bio',
      '.entry-content, .page-content, .post-content',
      '#about, #bio, #profile',
      'section:contains("About")'
    ];
    
    // First try common bio container selectors
    for (const selector of bioSelectors) {
      const bioElement = $(selector);
      if (bioElement.length) {
        // If we found a container, extract paragraphs from it
        bioContent = bioElement.find('p').map((_, el) => $(el).text().trim()).get().join('\n\n');
        if (bioContent) {
          console.log(`Found bio for ${therapistName} using selector ${selector} (${bioContent.length} chars)`);
          break;
        }
      }
    }
    
    // If we still don't have content, try to find an "About Me" section
    if (!bioContent) {
      // Look for headings that might indicate the start of a bio section
      $('h1, h2, h3, h4, h5').each((_, heading) => {
        const headingText = $(heading).text().trim();
        if (headingText.includes('About') || headingText.includes('Bio') || headingText.includes('Meet')) {
          // Found a potential bio section heading, collect paragraphs that follow it
          let paragraphs = [];
          let currentElement = $(heading).next();
          
          // Keep collecting paragraphs until we hit another heading or run out of elements
          while (currentElement.length && !currentElement.is('h1, h2, h3, h4, h5')) {
            if (currentElement.is('p')) {
              paragraphs.push(currentElement.text().trim());
            }
            currentElement = currentElement.next();
          }
          
          if (paragraphs.length) {
            bioContent = paragraphs.join('\n\n');
            console.log(`Found bio for ${therapistName} after heading "${headingText}" (${bioContent.length} chars)`);
            return false; // Break the each loop
          }
        }
      });
    }
    
    // If we still don't have content, try the main content area
    if (!bioContent) {
      const mainContent = $('.main-content, .content, article, main');
      if (mainContent.length) {
        // Get all paragraphs from main content
        const paragraphs = mainContent.find('p').map((_, el) => {
          const text = $(el).text().trim();
          // Filter out navigation text, contact info, etc.
          if (text.length > 50 && 
             !text.includes('call') && 
             !text.includes('Click') && 
             !text.includes('contact') && 
             !text.includes('schedule') && 
             !text.includes('appointment')) {
            return text;
          }
        }).get();
        
        if (paragraphs.length) {
          bioContent = paragraphs.join('\n\n');
          console.log(`Extracted ${paragraphs.length} paragraphs from main content for ${therapistName} (${bioContent.length} chars)`);
        }
      }
    }
    
    // Clean up the content
    bioContent = bioContent
      .replace(/\s+/g, ' ')
      .replace(/\n\s*\n/g, '\n\n')
      .trim();
    
    return bioContent;
  } catch (error) {
    console.error(`Error extracting bio for ${therapistName}: ${error.message}`);
    return '';
  }
}

/**
 * Scrape the team page to get basic therapist info
 */
async function scrapeTherapists() {
  console.log(`Fetching team page from ${THRIVE_TEAM_URL}...`);
  const html = await fetchUrl(THRIVE_TEAM_URL);
  const $ = cheerio.load(html);
  const therapists = [];

  // Look for therapist profile containers
  const therapistContainers = $('.team-member, .therapist, .provider, .staff-member, .person');
  
  if (therapistContainers.length === 0) {
    // If we don't find specific containers, try other common selectors
    console.log('No specific therapist containers found, trying alternative selectors');
    const alternativeContainers = $('article, .card, .profile, .bio-wrapper, .col').filter(function() {
      // Keep only elements that likely contain therapist info (image + heading)
      return $(this).find('img').length > 0 && $(this).find('h2, h3, h4, h5').length > 0;
    });
    
    if (alternativeContainers.length > 0) {
      console.log(`Found ${alternativeContainers.length} alternative therapist containers`);
      
      alternativeContainers.each((index, element) => {
        const el = $(element);
        const name = el.find('h2, h3, h4, h5').first().text().trim();
        const title = el.find('p, .title, .position').first().text().trim();
        const imageEl = el.find('img');
        let imageUrl = imageEl.attr('src') || imageEl.attr('data-src') || '';
        
        if (imageUrl && !imageUrl.startsWith('http')) {
          imageUrl = new URL(imageUrl, THRIVE_TEAM_URL).href;
        }
        
        // Look for "Read More" or bio link
        let bioLink = el.find('a:contains("Read More"), a:contains("read more"), a:contains("Bio"), a:contains("Learn More"), a:contains("Profile")').attr('href');
        
        // If no specific bio link found, look for any link that might lead to bio
        if (!bioLink) {
          const links = el.find('a');
          links.each((_, link) => {
            const href = $(link).attr('href');
            if (href && (href.includes(name.toLowerCase().replace(/\s+/g, '-')) || 
                        href.includes('/therapist/') || 
                        href.includes('/provider/') || 
                        href.includes('/team/'))) {
              bioLink = href;
              return false; // break the each loop
            }
          });
        }
        
        if (bioLink && !bioLink.startsWith('http')) {
          bioLink = new URL(bioLink, THRIVE_TEAM_URL).href;
        }
        
        if (name) {
          therapists.push({
            name,
            title: title || '',
            imageUrl,
            fullBioUrl: bioLink || '',
            bio: '' // Will be populated later
          });
        }
      });
    }
  } else {
    console.log(`Found ${therapistContainers.length} therapist containers`);
    
    // Extract data from each therapist container
    therapistContainers.each((index, element) => {
      const el = $(element);
      const name = el.find('h2, h3, h4, .name').first().text().trim();
      const title = el.find('.title, .position, .role, p').first().text().trim();
      const imageEl = el.find('img');
      let imageUrl = imageEl.attr('src') || imageEl.attr('data-src') || '';
      
      if (imageUrl && !imageUrl.startsWith('http')) {
        imageUrl = new URL(imageUrl, THRIVE_TEAM_URL).href;
      }
      
      // Look for "Read More" or bio link
      let bioLink = el.find('a:contains("Read More"), a:contains("read more"), a:contains("Bio"), a:contains("Learn More")').attr('href');
      
      // If no specific bio link found, look for any link that might lead to bio
      if (!bioLink) {
        const links = el.find('a');
        links.each((_, link) => {
          const href = $(link).attr('href');
          if (href && (href.includes(name.toLowerCase().replace(/\s+/g, '-')) || 
                      href.includes('/therapist/') || 
                      href.includes('/provider/') || 
                      href.includes('/team/'))) {
            bioLink = href;
            return false; // break the each loop
          }
        });
      }
      
      if (bioLink && !bioLink.startsWith('http')) {
        bioLink = new URL(bioLink, THRIVE_TEAM_URL).href;
      }
      
      if (name) {
        therapists.push({
          name,
          title: title || '',
          imageUrl,
          fullBioUrl: bioLink || '',
          bio: '' // Will be populated later
        });
      }
    });
  }

  console.log(`Found ${therapists.length} therapists`);
  return therapists;
}

/**
 * Download and save therapist image
 */
async function downloadImage(imageUrl, therapistName) {
  if (!imageUrl) {
    console.log(`No image URL for ${therapistName}`);
    return null;
  }
  
  try {
    // Create a sanitized filename from therapist name
    const sanitizedName = therapistName.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const extension = path.extname(new URL(imageUrl).pathname) || '.jpg';
    const filename = `${sanitizedName}${extension}`;
    const localPath = path.join(IMAGE_DIR, filename);
    
    // Check if file already exists
    if (fs.existsSync(localPath)) {
      console.log(`Image for ${therapistName} already exists at ${localPath}`);
      return `/images/therapists/${filename}`;
    }
    
    console.log(`Downloading image for ${therapistName} from ${imageUrl}`);
    
    // Download the image
    const response = await axios({
      method: 'GET',
      url: imageUrl,
      responseType: 'stream',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 15000
    });
    
    const writer = fs.createWriteStream(localPath);
    response.data.pipe(writer);
    
    return new Promise((resolve, reject) => {
      writer.on('finish', () => {
        console.log(`Downloaded image for ${therapistName} to ${localPath}`);
        resolve(`/images/therapists/${filename}`);
      });
      writer.on('error', (err) => {
        console.error(`Error writing image for ${therapistName}:`, err.message);
        reject(err);
      });
    });
  } catch (error) {
    console.error(`Error downloading image for ${therapistName}:`, error.message);
    return null;
  }
}

/**
 * Main function to extract all therapist data
 */
async function main() {
  try {
    console.log('Starting extraction of Thrive Counseling therapist data...');
    
    // Get basic therapist info from team page
    const therapists = await scrapeTherapists();
    
    if (therapists.length === 0) {
      throw new Error('No therapists found on the team page. Please check the selectors or URL.');
    }
    
    console.log(`Processing ${therapists.length} therapists...`);
    
    // For each therapist, fetch their detailed bio and download image
    for (const [index, therapist] of therapists.entries()) {
      console.log(`\n[${index+1}/${therapists.length}] Processing ${therapist.name}...`);
      
      // Fetch bio
      if (therapist.fullBioUrl) {
        console.log(`Fetching bio for ${therapist.name}...`);
        therapist.bio = await extractTherapistBio(therapist.fullBioUrl, therapist.name);
        console.log(`Bio length: ${therapist.bio.length} characters`);
      } else {
        console.log(`No bio URL for ${therapist.name}, skipping bio extraction`);
      }
      
      // Download image
      if (therapist.imageUrl) {
        therapist.localImagePath = await downloadImage(therapist.imageUrl, therapist.name);
      }
      
      // Add a delay between requests
      if (index < therapists.length - 1) {
        console.log(`Waiting ${DELAY_MS}ms before processing next therapist...`);
        await delay(DELAY_MS);
      }
    }
    
    // Save data as JSON backup
    fs.writeFileSync(OUTPUT_JSON, JSON.stringify(therapists, null, 2));
    console.log(`Saved JSON backup to ${OUTPUT_JSON}`);
    
    // Write data to CSV
    await csvWriter.writeRecords(therapists);
    console.log(`Successfully wrote data for ${therapists.length} therapists to ${OUTPUT_CSV}`);
    
    // Print summary
    console.log('\n=== Summary ===');
    console.log(`Total therapists found: ${therapists.length}`);
    console.log(`Therapists with bios: ${therapists.filter(t => t.bio && t.bio.length > 0).length}`);
    console.log(`Therapists with images: ${therapists.filter(t => t.localImagePath).length}`);
    console.log('=== Done ===');
    
  } catch (error) {
    console.error('\nError in main function:', error.message);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
}

// Run the script
main(); 