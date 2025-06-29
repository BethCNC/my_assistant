const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');
const { createObjectCsvWriter } = require('csv-writer');

// Base URL for the Thrive Counseling website
const BASE_URL = 'https://www.thrivecounselingnc.com';
const TEAM_URL = `${BASE_URL}/team`;
const IMAGE_DIR = path.join(__dirname, '..', 'public', 'images', 'therapists', 'thrive');

/**
 * Fetches HTML content from a URL
 * @param {string} url - The URL to fetch
 * @returns {Promise<string>} - The HTML content
 */
async function fetchHTML(url) {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${url}:`, error.message);
    return null;
  }
}

/**
 * Downloads an image from a URL and saves it locally
 * @param {string} imageUrl - The URL of the image
 * @param {string} therapistName - The name of the therapist (for filename)
 * @returns {Promise<string|null>} - The path where the image was saved, or null if failed
 */
async function downloadImage(imageUrl, therapistName) {
  try {
    // Make sure the directory exists
    if (!fs.existsSync(IMAGE_DIR)) {
      fs.mkdirSync(IMAGE_DIR, { recursive: true });
    }

    // Generate a filename from the therapist's name
    const fileName = therapistName.toLowerCase().replace(/\s+/g, '-') + '.jpg';
    const filePath = path.join(IMAGE_DIR, fileName);
    
    // Download the image
    const response = await axios({
      url: imageUrl,
      method: 'GET',
      responseType: 'stream'
    });
    
    // Save the image to file
    const writer = fs.createWriteStream(filePath);
    response.data.pipe(writer);
    
    return new Promise((resolve, reject) => {
      writer.on('finish', () => resolve(filePath));
      writer.on('error', reject);
    });
  } catch (error) {
    console.error(`Error downloading image for ${therapistName}:`, error.message);
    return null;
  }
}

/**
 * Extracts the full bio from a therapist's detail page
 * @param {string} detailUrl - URL of the therapist's detail page
 * @param {string} therapistName - Name of the therapist
 * @returns {Promise<string>} - The full bio text
 */
async function getFullBio(detailUrl, therapistName) {
  try {
    const html = await fetchHTML(detailUrl);
    if (!html) return '';
    
    const $ = cheerio.load(html);
    
    // Try different selectors to find the bio content
    // Looking for common content containers
    let bioText = '';
    
    // Try various selectors that might contain the bio content
    const selectors = [
      '.bio-content', 
      '.therapist-bio', 
      '.about-content',
      '.staff-bio',
      '.content-area',
      '.main-content',
      'article',
      '.entry-content'
    ];
    
    for (const selector of selectors) {
      const content = $(selector).text();
      if (content && content.trim().length > bioText.length) {
        bioText = content.trim();
      }
    }
    
    // If we didn't find anything with specific selectors, try a more general approach
    if (!bioText) {
      // Look for paragraphs within the main content area
      const mainContent = $('main').length ? $('main') : $('body');
      let paragraphs = '';
      mainContent.find('p').each((i, el) => {
        paragraphs += $(el).text() + '\n\n';
      });
      
      if (paragraphs.trim().length > 0) {
        bioText = paragraphs.trim();
      }
    }
    
    // Clean up the text
    return bioText
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim();
  } catch (error) {
    console.error(`Error getting full bio for ${therapistName}:`, error.message);
    return '';
  }
}

/**
 * Scrapes therapist data from the Thrive Counseling website
 * @returns {Promise<Array>} - Array of therapist data objects
 */
async function scrapeThriveCounselingTherapists() {
  try {
    console.log('Fetching team page from Thrive Counseling...');
    const html = await fetchHTML(TEAM_URL);
    if (!html) {
      console.error('Failed to fetch the team page');
      return [];
    }
    
    const $ = cheerio.load(html);
    const therapists = [];
    
    // Find all therapist sections
    // Each therapist section typically contains:
    // - Name/title (in a heading element)
    // - Role/subtitle 
    // - Short bio excerpt
    // - "Read More" link to their individual page
    // - Image
    
    // On the Thrive Counseling site, therapists are listed with h2 headings
    const therapistSections = $('h2').closest('div');
    
    console.log(`Found ${therapistSections.length} potential therapist sections`);
    
    for (let i = 0; i < therapistSections.length; i++) {
      const section = therapistSections[i];
      
      // Extract therapist name
      const nameElement = $(section).find('h2');
      if (!nameElement.length) continue;
      
      const name = nameElement.text().trim();
      console.log(`Processing therapist: ${name}`);
      
      // Skip if doesn't look like a therapist name (e.g., headings for other sections)
      if (!name || name.toLowerCase().includes('location')) continue;
      
      // Extract the role/title
      const roleElement = $(section).find('h3, p').first();
      const role = roleElement.length ? roleElement.text().trim() : '';
      
      // Extract the short bio
      let bioExcerpt = '';
      $(section).find('p').each((j, el) => {
        if (j > 0) { // Skip the first p tag which might be the role
          bioExcerpt += $(el).text().trim() + ' ';
        }
      });
      bioExcerpt = bioExcerpt.trim();
      
      // Find the "Read More" link
      const readMoreLink = $(section).find('a:contains("Read More")');
      let detailUrl = '';
      if (readMoreLink.length) {
        const href = readMoreLink.attr('href');
        detailUrl = href.startsWith('http') ? href : `${BASE_URL}${href}`;
      }
      
      // If we couldn't find a "Read More" link, try to construct the URL based on pattern
      if (!detailUrl) {
        const formattedName = name.split(',')[0].toLowerCase().replace(/\s+/g, '-');
        detailUrl = `${BASE_URL}/staff-member/${formattedName}`;
      }
      
      // Extract image URL
      let imageUrl = '';
      const imgElement = $(section).find('img');
      if (imgElement.length) {
        const src = imgElement.attr('src');
        imageUrl = src.startsWith('http') ? src : `${BASE_URL}${src}`;
      }
      
      // Get the full bio from the detail page
      console.log(`Fetching full bio from: ${detailUrl}`);
      const fullBio = await getFullBio(detailUrl, name);
      
      // Download the image if available
      let imagePath = null;
      if (imageUrl) {
        console.log(`Downloading image for ${name} from: ${imageUrl}`);
        imagePath = await downloadImage(imageUrl, name);
      }
      
      // Create therapist object
      const therapist = {
        name,
        role,
        bioExcerpt,
        fullBio,
        detailUrl,
        imageUrl,
        localImagePath: imagePath
      };
      
      therapists.push(therapist);
      console.log(`Added ${name} to results`);
    }
    
    return therapists;
  } catch (error) {
    console.error('Error scraping therapist data:', error);
    return [];
  }
}

/**
 * Main function to run the scraper and write results to CSV
 */
async function main() {
  try {
    console.log('Starting scraper for Thrive Counseling therapists...');
    
    // Scrape therapist data
    const therapists = await scrapeThriveCounselingTherapists();
    console.log(`Scraped data for ${therapists.length} therapists`);
    
    // Write therapist data to CSV
    const csvWriter = createObjectCsvWriter({
      path: path.join(__dirname, '..', 'data', 'thrive-therapists.csv'),
      header: [
        { id: 'name', title: 'Name' },
        { id: 'role', title: 'Role' },
        { id: 'bioExcerpt', title: 'Bio Excerpt' },
        { id: 'fullBio', title: 'Full Bio' },
        { id: 'detailUrl', title: 'Detail URL' },
        { id: 'imageUrl', title: 'Image URL' },
        { id: 'localImagePath', title: 'Local Image Path' }
      ]
    });
    
    await csvWriter.writeRecords(therapists);
    console.log('CSV file has been written successfully');
    
    // Save raw data as JSON for backup/debugging
    fs.writeFileSync(
      path.join(__dirname, '..', 'data', 'thrive-therapists.json'),
      JSON.stringify(therapists, null, 2)
    );
    console.log('JSON file has been written successfully');
    
    console.log('Scraping complete');
  } catch (error) {
    console.error('Error in main function:', error);
  }
}

// Run the main function if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = {
  scrapeThriveCounselingTherapists
}; 