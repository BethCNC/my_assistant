require('dotenv').config();
const { Client } = require('@notionhq/client');
const axios = require('axios');
const cheerio = require('cheerio');

// Initialize Notion client
const notion = new Client({
  auth: process.env.NOTION_TOKEN,
});

// Use database ID from .env if available, otherwise use the one from therapist-rules.mdc
const databaseId = process.env.THERAPIST_DB_ID || '1d586edcae2c8035b63ac880990ace27';

// Target websites from the therapist-rules.mdc
const websites = [
  {
    name: 'Glenda Vinson Nnaji - Psychology Today',
    url: 'https://www.psychologytoday.com/us/therapists/glenda-vinson-nnaji-matthews-nc/282119',
    group: 'Private',
    type: 'individual'
  },
  {
    name: 'Reaching Resolution',
    url: 'https://www.reachingresolution.net/meet-the-team',
    group: 'Reaching Resolution',
    type: 'group'
  },
  {
    name: 'Myriam Rabaste - NeuroNNection',
    url: 'https://neuronnection.com/profile/',
    group: 'NeuroConnection',
    type: 'individual'
  },
  {
    name: 'Thrive Counseling',
    url: 'https://www.thrivecounselingnc.com/team',
    group: 'Thrive Counseling',
    type: 'group'
  },
  {
    name: 'Anna Thames Counseling',
    url: 'https://www.annathamescounseling.com/team',
    group: 'Anna Thames Counseling',
    type: 'group'
  }
];

// Helper function to split long text into chunks of 2000 characters or less
function splitLongText(text) {
  if (!text || text.length <= 2000) {
    return [text || ""];
  }
  
  const chunks = [];
  let remainingText = text;
  
  while (remainingText.length > 0) {
    // Find a good split point - prefer splitting at paragraph breaks
    let splitIndex = 1999;
    if (remainingText.length > 2000) {
      // Look for paragraph break before the 2000 character limit
      const lastParagraphBreak = remainingText.lastIndexOf('\n\n', 1999);
      if (lastParagraphBreak > 0) {
        splitIndex = lastParagraphBreak + 2; // Include the paragraph break
      } else {
        // If no paragraph break, look for sentence end
        const lastSentenceBreak = remainingText.lastIndexOf('. ', 1999);
        if (lastSentenceBreak > 0) {
          splitIndex = lastSentenceBreak + 2; // Include the period and space
        }
      }
    } else {
      splitIndex = remainingText.length;
    }
    
    chunks.push(remainingText.substring(0, splitIndex));
    remainingText = remainingText.substring(splitIndex);
  }
  
  return chunks;
}

// Create a new therapist entry in the Notion database
async function createTherapistEntry(therapist) {
  try {
    // Skip therapists with no name
    if (!therapist.name || therapist.name.trim() === '') {
      console.log('Skipping entry with empty name');
      return;
    }

    // Ensure group is set
    if (!therapist.group) {
      console.warn(`Warning: No group specified for therapist ${therapist.name}`);
      therapist.group = 'Unknown';
    }

    const properties = {
      Name: {
        title: [
          {
            text: {
              content: therapist.name
            }
          }
        ]
      },
      "Office/Group": {
        multi_select: [
          {
            name: therapist.group
          }
        ]
      },
      "Mom": {
        select: {
          name: "No"
        }
      },
      "Final Vote": {
        select: {
          name: "??"
        }
      }
    };
    
    // Add Bio if available
    if (therapist.bio) {
      properties.Bio = {
        rich_text: [
          {
            text: {
              content: therapist.bio.slice(0, 2000) // Notion has a limit on rich_text
            }
          }
        ]
      };
    }
    
    // Add Notes if available
    if (therapist.notes) {
      properties.Notes = {
        rich_text: [
          {
            text: {
              content: therapist.notes.slice(0, 2000)
            }
          }
        ]
      };
    }

    // Add Address if available
    if (therapist.location) {
      properties.Address = {
        rich_text: [
          {
            text: {
              content: therapist.location
            }
          }
        ]
      };
    }

    // Add Email if available
    if (therapist.email) {
      properties.Email = {
        email: therapist.email
      };
    }

    // Add Phone Number if available
    if (therapist.phone) {
      properties["Phone Number"] = {
        phone_number: therapist.phone
      };
    }

    // Add URL if available
    if (therapist.url) {
      properties.URL = {
        url: therapist.url
      };
    }

    // Set Telehealth if available
    if (therapist.telehealth) {
      properties["Telehealth?"] = {
        select: {
          name: therapist.telehealth === true ? "Yes" : "No"
        }
      };
    }

    // Set BCBS if available
    if (therapist.bcbs !== undefined) {
      properties.BCBS = {
        select: {
          name: therapist.bcbs === true ? "Yes" : "No"
        }
      };
    }

    // Set EMDR if available
    if (therapist.emdr !== undefined) {
      properties.EMDR = {
        select: {
          name: therapist.emdr === true ? "Yes" : "No"
        }
      };
    }

    console.log(`Creating entry with properties: `, {
      Name: properties.Name,
      "Office/Group": properties["Office/Group"],
      Bio: properties.Bio ? "Provided" : "Not provided",
      Telehealth: properties["Telehealth?"] ? properties["Telehealth?"].select.name : "Not specified",
      BCBS: properties.BCBS ? properties.BCBS.select.name : "Not specified",
      EMDR: properties.EMDR ? properties.EMDR.select.name : "Not specified"
    });

    const response = await notion.pages.create({
      parent: {
        database_id: databaseId,
      },
      properties: properties
    });
    
    console.log(`Created entry for ${therapist.name} with group ${therapist.group}`);
    return response;
  } catch (error) {
    console.error(`Error creating entry for ${therapist.name}:`, error.message);
    throw error;
  }
}

// Extract therapist info from Psychology Today
async function extractFromPsychologyToday(website) {
  try {
    console.log(`Scraping data from Psychology Today: ${website.url}`);
    const response = await axios.get(website.url);
    const $ = cheerio.load(response.data);
    
    // Extract therapist name
    const name = $('h1.profile-name').text().trim();
    console.log(`Found therapist name: ${name}`);
    
    if (!name) {
      console.error('Failed to extract therapist name from Psychology Today');
      return [];
    }
    
    // Extract location - Psychology Today typically has structured address fields
    const location = $('.location-address').text().trim();
    console.log(`Found location: ${location || 'Not available'}`);
    
    // Extract bio
    const bio = $('.profile-detail[data-handle="about"]').text().trim();
    
    // Extract specialties and notes
    const specialties = $('.profile-detail[data-handle="specialties"] .spec-list').text().trim();
    const treatmentApproach = $('.profile-detail[data-handle="treatment-approach"] .spec-list').text().trim();
    
    // Additional notes
    const qualifications = $('.profile-detail[data-handle="qualifications"]').text().trim();
    const finances = $('.profile-detail[data-handle="finances"]').text().trim();
    
    const notes = `Specialties: ${specialties}\n\nTreatment Approach: ${treatmentApproach}\n\nQualifications: ${qualifications}\n\nFinances: ${finances}`;
    
    // Check for BCBS with more detailed analysis
    let bcbs = "Unknown";
    const financesLower = finances.toLowerCase();
    if (financesLower.includes('blue cross') || financesLower.includes('bcbs')) {
      if (financesLower.includes('not accept') || financesLower.includes('don\'t accept') || financesLower.includes('do not accept')) {
        bcbs = "No";
      } else {
        bcbs = "Yes";
      }
    }
    console.log(`BCBS status: ${bcbs}`);
    
    // Check for EMDR
    const emdr = treatmentApproach.toLowerCase().includes('emdr') ? "Yes" : "No";
    
    // Check for telehealth with more detailed analysis
    let telehealth = "Unknown";
    
    // Psychology Today often has specific sections for session format
    const sessionFormatSection = $('.profile-detail:contains("Session Format")').text().toLowerCase();
    
    if (sessionFormatSection) {
      if (sessionFormatSection.includes('in person') && (sessionFormatSection.includes('online') || sessionFormatSection.includes('virtual') || sessionFormatSection.includes('telehealth'))) {
        telehealth = "Both";
      } else if (sessionFormatSection.includes('online only') || sessionFormatSection.includes('virtual only') || sessionFormatSection.includes('telehealth only')) {
        telehealth = "Yes";
      } else if (sessionFormatSection.includes('in person only')) {
        telehealth = "No";
      } else if (sessionFormatSection.includes('online') || sessionFormatSection.includes('virtual') || sessionFormatSection.includes('telehealth')) {
        telehealth = "Yes";
      } else if (sessionFormatSection.includes('in person')) {
        telehealth = "No";
      }
    } else {
      // Fall back to checking the finances section if no dedicated session format section
      if (financesLower.includes('in person') && (financesLower.includes('online') || financesLower.includes('virtual') || financesLower.includes('telehealth'))) {
        telehealth = "Both";
      } else if (financesLower.includes('online only') || financesLower.includes('virtual only') || financesLower.includes('telehealth only')) {
        telehealth = "Yes";
      } else if (financesLower.includes('in person only')) {
        telehealth = "No";
      } else if (financesLower.includes('online') || financesLower.includes('virtual') || financesLower.includes('telehealth')) {
        telehealth = "Yes";
      } else if (financesLower.includes('in person')) {
        telehealth = "No";
      }
    }
    console.log(`Telehealth status: ${telehealth}`);
    
    // Extract phone - Psychology Today usually has a dedicated phone element
    const phone = $('.profile-phone').text().trim();
    console.log(`Phone: ${phone || 'Not available'}`);
    
    // Extract email if available
    const email = $('.profile-email a').attr('href')?.replace('mailto:', '') || '';
    console.log(`Email: ${email || 'Not available'}`);
    
    return [{
      name,
      group: website.group,
      location,
      bio,
      notes,
      phone,
      email,
      url: website.url,
      bcbs,
      emdr,
      telehealth
    }];
  } catch (error) {
    console.error(`Error extracting from Psychology Today:`, error.message);
    return [];
  }
}

// Fix Reaching Resolution extraction function URLs and selectors
async function extractFromReachingResolution(website) {
  try {
    console.log(`Scraping data from Reaching Resolution: ${website.url}`);
    const response = await axios.get(website.url);
    const $ = cheerio.load(response.data);
    
    const therapists = [];
    
    // Website info for all therapists
    let officeAddress = "3095 Senna Dr, Matthews, NC 28105"; // Hardcoded from the footer
    let officePhone = "(980) 999-4787"; // Hardcoded from the page
    
    // Try to get contact information from the main page if not hardcoded
    if (!officePhone) {
      const phoneRegex = /(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/;
      const allText = $('body').text();
      const phoneMatch = allText.match(phoneRegex);
      if (phoneMatch) officePhone = phoneMatch[0];
    }
    
    // Default BCBS and telehealth values
    let bcbsOfficeInfo = "Yes"; // Default based on research
    let telehealthOfficeInfo = "Yes"; // Default as they mention telehealth/teleplay therapy
    
    // Find each therapist using the "Learn more about" sections
    const therapistSections = $('*:contains("Learn more about")');
    console.log(`Found ${therapistSections.length} potential therapist sections`);
    
    if (therapistSections.length > 0) {
      therapistSections.each((i, section) => {
        try {
          const text = $(section).text().trim();
          const nameMatch = text.match(/Learn more about (\w+)/i);
          
          if (nameMatch && nameMatch[1]) {
            const firstName = nameMatch[1];
            
            // Find the heading above this section which should contain the full name
            const parentEl = $(section).parent();
            const heading = parentEl.prev('h2, h3, h4, h5');
            const fullName = heading.text().trim();
            
            if (fullName) {
              console.log(`Found therapist: ${fullName}`);
              
              // Find the nearest paragraph for bio
              let bio = '';
              const paragraphs = parentEl.find('p');
              if (paragraphs.length > 0) {
                bio = paragraphs.text().trim();
              }
              
              // If no bio found, look at sibling elements
              if (!bio) {
                const siblingParagraphs = parentEl.siblings('p');
                if (siblingParagraphs.length > 0) {
                  bio = siblingParagraphs.text().trim();
                }
              }
              
              // Check for EMDR specific to this therapist
              const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
              
              // Check for therapist-specific BCBS info (use office default if not found)
              let bcbs = bcbsOfficeInfo;
              if (bio.toLowerCase().includes('blue cross') || bio.toLowerCase().includes('bcbs')) {
                if (bio.toLowerCase().includes('not accept') || bio.toLowerCase().includes('don\'t accept') || bio.toLowerCase().includes('do not accept')) {
                  bcbs = "No";
                } else {
                  bcbs = "Yes";
                }
              }
              
              // Check for therapist-specific telehealth info (use office default if not found)
              let telehealth = telehealthOfficeInfo;
              const bioLower = bio.toLowerCase();
              if (bioLower.includes('telehealth') || bioLower.includes('virtual') || bioLower.includes('online')) {
                telehealth = "Yes";
                
                // Check if in-person is also mentioned for this therapist
                if (bioLower.includes('in person') || bioLower.includes('in-person') || bioLower.includes('office visit')) {
                  telehealth = "Both";
                }
              } else if (bioLower.includes('in person only') || bioLower.includes('in-person only') || bioLower.includes('office only')) {
                telehealth = "No";
              }
              
              therapists.push({
                name: fullName,
                group: website.group,
                location: officeAddress,
                bio,
                notes: '', 
                phone: officePhone,
                email: '', // No emails visible on the page
                url: website.url,
                bcbs,
                emdr,
                telehealth
              });
            }
          }
        } catch (error) {
          console.error(`Error extracting individual therapist:`, error.message);
        }
      });
    }
    
    // If no therapists found with the primary method, try alternative selectors
    if (therapists.length === 0) {
      console.log("No therapists found with primary method, trying alternative approach");
      
      // Look for headings that contain therapist names
      const headings = $('h2, h3, h4, h5').filter(function() {
        const text = $(this).text().trim();
        // Look for patterns like "Dr. Name" or "Name, Credentials"
        return text.includes('Dr.') || text.includes('LCMHC') || text.includes('LCSW') || text.includes('MA,');
      });
      
      console.log(`Found ${headings.length} potential therapist headings`);
      
      headings.each((i, heading) => {
        try {
          const fullName = $(heading).text().trim();
          
          // Clean up credentials from the name if they exist
          let name = fullName;
          const credentialsMatch = fullName.match(/(.*?),\s+[A-Z]+/);
          if (credentialsMatch) {
            name = credentialsMatch[1].trim();
          }
          
          console.log(`Found therapist: ${name}`);
          
          // Get bio from following paragraph or div
          let bio = '';
          const nextEl = $(heading).next('p, div');
          if (nextEl.length > 0) {
            bio = nextEl.text().trim();
          }
          
          // Check for EMDR, BCBS, and telehealth in bio
          const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
          let bcbs = bcbsOfficeInfo;
          let telehealth = telehealthOfficeInfo;
          
          therapists.push({
            name,
            group: website.group,
            location: officeAddress,
            bio,
            notes: '', 
            phone: officePhone,
            email: '', 
            url: website.url,
            bcbs,
            emdr,
            telehealth
          });
        } catch (error) {
          console.error(`Error extracting individual therapist:`, error.message);
        }
      });
    }
    
    return therapists;
  } catch (error) {
    console.error(`Error extracting from Reaching Resolution:`, error.message);
    return [];
  }
}

// Extract therapist info from Neuro Connection
async function extractFromNeuroConnection(website) {
  try {
    console.log(`Scraping data from Neuro Connection: ${website.url}`);
    const response = await axios.get(website.url);
    const $ = cheerio.load(response.data);
    
    // Get office-wide contact info
    let officeAddress = "";
    let officePhone = "";
    
    // Get the address from the footer
    const footerAddress = $('.footer-address').text().trim();
    if (footerAddress) {
      officeAddress = footerAddress;
      console.log(`Found office address from footer: ${officeAddress}`);
    }
    
    // Get the phone from the footer or contact section
    const footerPhone = $('.footer-phone, .contact-phone').text().trim();
    if (footerPhone) {
      officePhone = footerPhone;
      console.log(`Found office phone from footer: ${officePhone}`);
    } else {
      // Try to match phone pattern in the page
      const phoneRegex = /(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/;
      const allText = $('body').text();
      const phoneMatch = allText.match(phoneRegex);
      if (phoneMatch) officePhone = phoneMatch[0];
    }
    
    // If direct elements not found, try to visit contact page
    if (!officeAddress || !officePhone) {
      try {
        const contactUrl = `${new URL(website.url).origin}/contact`;
        console.log(`Getting contact info from: ${contactUrl}`);
        const contactResponse = await axios.get(contactUrl);
        const contact$ = cheerio.load(contactResponse.data);
        
        // Look for address
        if (!officeAddress) {
          const addressEl = contact$('.contact-address, address');
          if (addressEl.length) {
            officeAddress = addressEl.text().trim();
            console.log(`Found office address from contact page: ${officeAddress}`);
          }
        }
        
        // Look for phone
        if (!officePhone) {
          const phoneEl = contact$('.contact-phone, .phone');
          if (phoneEl.length) {
            officePhone = phoneEl.text().trim();
            console.log(`Found office phone from contact page: ${officePhone}`);
          } else {
            // Try to match phone pattern
            const contactText = contact$('body').text();
            const phoneMatch = contactText.match(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
            if (phoneMatch) {
              officePhone = phoneMatch[0];
              console.log(`Found office phone from contact page text: ${officePhone}`);
            }
          }
        }
      } catch (error) {
        console.error('Error getting contact page info:', error.message);
      }
    }
    
    // Check for insurance and telehealth info from insurance/faq page
    let officeAcceptsBCBS = "Unknown";
    let officeTelehealth = "Unknown";
    
    try {
      // Try insurance page
      const insuranceUrl = `${new URL(website.url).origin}/insurance`;
      console.log(`Getting insurance info from: ${insuranceUrl}`);
      
      const insuranceResponse = await axios.get(insuranceUrl);
      const insurance$ = cheerio.load(insuranceResponse.data);
      
      const insuranceText = insurance$('body').text().toLowerCase();
      
      // Check for BCBS mentions
      if (insuranceText.includes('blue cross') || insuranceText.includes('bcbs')) {
        if (insuranceText.includes('not accept') || insuranceText.includes('don\'t accept') || insuranceText.includes('do not accept')) {
          officeAcceptsBCBS = "No";
        } else {
          officeAcceptsBCBS = "Yes";
        }
        console.log(`Found BCBS info from insurance page: ${officeAcceptsBCBS}`);
      }
      
      // Check for telehealth mentions
      if (insuranceText.includes('telehealth') || insuranceText.includes('virtual') || insuranceText.includes('remote') || insuranceText.includes('online')) {
        officeTelehealth = "Yes";
        
        // Check if in-person is also mentioned
        if (insuranceText.includes('in person') || insuranceText.includes('in-person') || insuranceText.includes('office')) {
          officeTelehealth = "Both";
        }
        console.log(`Found telehealth info from insurance page: ${officeTelehealth}`);
      } else if (insuranceText.includes('in person only') || insuranceText.includes('in-person only') || insuranceText.includes('office visits only')) {
        officeTelehealth = "No";
        console.log(`Found telehealth info from insurance page: ${officeTelehealth}`);
      }
    } catch (error) {
      // Try FAQ page if insurance page fails
      try {
        const faqUrl = `${new URL(website.url).origin}/faq`;
        console.log(`Getting info from FAQ page: ${faqUrl}`);
        
        const faqResponse = await axios.get(faqUrl);
        const faq$ = cheerio.load(faqResponse.data);
        
        const faqText = faq$('body').text().toLowerCase();
        
        // Check for BCBS in FAQ
        if (faqText.includes('blue cross') || faqText.includes('bcbs')) {
          if (faqText.includes('not accept') || faqText.includes('don\'t accept') || faqText.includes('do not accept')) {
            officeAcceptsBCBS = "No";
          } else {
            officeAcceptsBCBS = "Yes";
          }
          console.log(`Found BCBS info from FAQ page: ${officeAcceptsBCBS}`);
        }
        
        // Check for telehealth in FAQ
        if (faqText.includes('telehealth') || faqText.includes('virtual') || faqText.includes('remote') || faqText.includes('online')) {
          officeTelehealth = "Yes";
          
          // Check if in-person is also mentioned
          if (faqText.includes('in person') || faqText.includes('in-person') || faqText.includes('office')) {
            officeTelehealth = "Both";
          }
          console.log(`Found telehealth info from FAQ page: ${officeTelehealth}`);
        } else if (faqText.includes('in person only') || faqText.includes('in-person only') || faqText.includes('office visits only')) {
          officeTelehealth = "No";
          console.log(`Found telehealth info from FAQ page: ${officeTelehealth}`);
        }
      } catch (faqError) {
        console.error('Error getting FAQ page info:', faqError.message);
      }
    }
    
    const therapists = [];
    // Find therapist sections - typically staff or team sections
    const staffDivs = $('.staff-member, .team-member, .therapist, .provider');
    
    if (staffDivs.length > 0) {
      staffDivs.each((i, div) => {
        try {
          // Extract therapist name
          const name = $(div).find('h3').text().trim();
          
          // Extract bio text
          const bio = $(div).find('p').text().trim();
          
          // Check for EMDR specific to this therapist
          const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
          
          // Extract therapist-specific contact information (if available)
          let therapistPhone = $(div).find('.phone').text().trim() || officePhone;
          let therapistEmail = "";
          
          // Look for email in bio
          const emailRegex = /[\w.-]+@[\w.-]+\.\w+/;
          const emailMatch = bio.match(emailRegex);
          if (emailMatch) therapistEmail = emailMatch[0];
          
          // Check for therapist-specific BCBS info
          let bcbs = bcbsOfficeInfo;
          if (bio.toLowerCase().includes('blue cross') || bio.toLowerCase().includes('bcbs')) {
            if (bio.toLowerCase().includes('not accept') || bio.toLowerCase().includes('don\'t accept') || bio.toLowerCase().includes('do not accept')) {
              bcbs = "No";
            } else {
              bcbs = "Yes";
            }
          }
          
          // Check for therapist-specific telehealth info
          let telehealth = telehealthOfficeInfo;
          const bioLower = bio.toLowerCase();
          if (bioLower.includes('telehealth') || bioLower.includes('virtual') || bioLower.includes('online')) {
            telehealth = "Yes";
            
            // Check if in-person is also mentioned for this therapist
            if (bioLower.includes('in person') || bioLower.includes('in-person') || bioLower.includes('office visit')) {
              telehealth = "Both";
            }
          } else if (bioLower.includes('in person only') || bioLower.includes('in-person only') || bioLower.includes('office only')) {
            telehealth = "No";
          }
          
          console.log(`Found therapist: ${name}`);
          console.log(`  EMDR: ${emdr}`);
          console.log(`  BCBS: ${bcbs}`);
          console.log(`  Telehealth: ${telehealth}`);
          console.log(`  Phone: ${therapistPhone}`);
          console.log(`  Email: ${therapistEmail}`);
          
          therapists.push({
            name,
            group: website.group,
            location: officeAddress,
            bio,
            notes: '', 
            phone: therapistPhone,
            email: therapistEmail,
            url: website.url,
            bcbs,
            emdr,
            telehealth
          });
        } catch (error) {
          console.error(`Error extracting individual therapist:`, error.message);
        }
      });
    } else {
      console.log('No therapist elements found. Trying alternative selectors');
      // Try alternative approaches - sometimes therapists are listed in a different format
      const allTherapistSections = $('section:contains("Our Team"), section:contains("Meet Our"), section:contains("Therapists")');
      
      if (allTherapistSections.length > 0) {
        // Look for therapist names in headings within these sections
        const headings = allTherapistSections.find('h2, h3, h4').filter(function() {
          const text = $(this).text().trim();
          // Filter out section titles
          return text !== "Our Team" && text !== "Meet Our Team" && text !== "Therapists" && text.length > 0;
        });
        
        headings.each((i, heading) => {
          try {
            const name = $(heading).text().trim();
            // Try to get bio - might be in sibling paragraph or div
            let bio = "";
            let currElement = heading;
            
            // Look for bio in next elements
            while ((currElement = $(currElement).next()) && currElement.length > 0) {
              // Stop if we hit another heading
              if (currElement.is('h2, h3, h4')) break;
              
              // Add text from paragraphs
              if (currElement.is('p') || currElement.is('div:not(:has(h2, h3, h4))')) {
                bio += (bio ? "\n\n" : "") + currElement.text().trim();
              }
            }
            
            // Check for EMDR
            const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
            
            // Look for therapist-specific contact information
            let email = "";
            let phone = officePhone;
            
            // Try to find email
            const emailMatch = bio.match(/[\w.-]+@[\w.-]+\.\w+/);
            if (emailMatch) {
              email = emailMatch[0];
            }
            
            // Try to find phone
            const phoneMatch = bio.match(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
            if (phoneMatch) {
              phone = phoneMatch[0];
            }
            
            // Check for BCBS and telehealth
            let bcbs = officeAcceptsBCBS;
            let telehealth = officeTelehealth;
            
            const bioLower = bio.toLowerCase();
            
            // Override BCBS if mentioned in bio
            if (bioLower.includes('blue cross') || bioLower.includes('bcbs')) {
              if (bioLower.includes('not accept') || bioLower.includes('don\'t accept') || bioLower.includes('do not accept')) {
                bcbs = "No";
              } else {
                bcbs = "Yes";
              }
            }
            
            // Override telehealth if mentioned in bio
            if (bioLower.includes('telehealth') || bioLower.includes('virtual') || bioLower.includes('online')) {
              telehealth = "Yes";
              
              // Check if in-person is also mentioned
              if (bioLower.includes('in person') || bioLower.includes('in-person') || bioLower.includes('office visit')) {
                telehealth = "Both";
              }
            } else if (bioLower.includes('in person only') || bioLower.includes('in-person only') || bioLower.includes('office only')) {
              telehealth = "No";
            }
            
            console.log(`Found therapist: ${name}`);
            console.log(`  Email: ${email || 'Not available'}`);
            console.log(`  Phone: ${phone || 'Not available'}`);
            console.log(`  EMDR: ${emdr}`);
            console.log(`  BCBS: ${bcbs}`);
            console.log(`  Telehealth: ${telehealth}`);
            
            therapists.push({
              name,
              group: website.group,
              location: officeAddress,
              bio,
              notes: '',
              phone,
              email,
              url: website.url,
              bcbs,
              emdr,
              telehealth
            });
          } catch (error) {
            console.error(`Error extracting individual therapist from headings:`, error.message);
          }
        });
      }
    }
    
    if (therapists.length === 0) {
      console.log('No therapists found using any method');
    }
    
    return therapists;
  } catch (error) {
    console.error(`Error extracting from Neuro Connection:`, error.message);
    return [];
  }
}

// Fix Thrive Counseling extraction function
async function extractFromThriveCounseling(website) {
  try {
    console.log(`Scraping data from Thrive Counseling: ${website.url}`);
    const response = await axios.get(website.url);
    const $ = cheerio.load(response.data);
    
    const therapists = [];
    
    // Get office address from the footer
    let officeAddress = '';
    // Try to find address in footer
    const footerText = $('footer').text().trim();
    const addressMatch = footerText.match(/(Monroe, NC|Indian Trail, NC|Waxhaw, NC)[\s\S]*?\d{5}/g);
    if (addressMatch) {
      officeAddress = addressMatch[0].trim();
      console.log(`Found office address from footer: ${officeAddress}`);
    } else {
      // Hardcode based on the footer info
      officeAddress = "Monroe, Indian Trail, and Waxhaw, NC";
    }
    
    // Get office phone - most likely in header or footer
    let officePhone = '';
    const phoneRegex = /(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/;
    const headerText = $('header').text().trim();
    const phoneMatch = headerText.match(phoneRegex);
    if (phoneMatch) {
      officePhone = phoneMatch[0].trim();
      console.log(`Found office phone: ${officePhone}`);
    } else {
      // Try to find in the whole page
      const pageText = $('body').text();
      const pagePhoneMatch = pageText.match(phoneRegex);
      if (pagePhoneMatch) {
        officePhone = pagePhoneMatch[0].trim();
        console.log(`Found office phone from page: ${officePhone}`);
      } else {
        // Hardcode based on the page header
        officePhone = "(704) 438-9901";
      }
    }
    
    // Default values for BCBS and telehealth
    let officeAcceptsBCBS = "Yes"; // Default based on common practice
    let officeTelehealth = "Yes"; // Default based on the times
    
    // Find therapist cards - try different selector patterns
    const therapistCards = $('.team-member, .staff-member, div[class*="team"], div[class*="staff"]');
    console.log(`Found ${therapistCards.length} potential therapist cards`);
    
    if (therapistCards.length > 0) {
      therapistCards.each((i, card) => {
        try {
          // Find name - look for headings inside the card
          const nameEl = $(card).find('h2, h3, h4, h5');
          if (nameEl.length === 0) return;
          
          const name = nameEl.first().text().trim();
          if (!name) return;
          
          console.log(`Found therapist: ${name}`);
          
          // Find bio - look for paragraphs or divs with text
          let bio = '';
          const bioParagraphs = $(card).find('p');
          if (bioParagraphs.length > 0) {
            bio = bioParagraphs.text().trim();
          }
          
          // If no bio found, try to find "Read More" links or expand buttons
          if (!bio || bio.length < 50) {
            const readMoreLink = $(card).find('a:contains("Read More")');
            if (readMoreLink.length > 0) {
              // Extract expanded text if available
              const expandedBioContainer = $(card).find('.expanded-bio, .full-bio, .bio-expanded');
              if (expandedBioContainer.length > 0) {
                bio = expandedBioContainer.text().trim();
              }
            }
          }
          
          // Check for EMDR mention in bio
          const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
          
          // Check for BCBS mention in bio or use office-wide value
          let bcbs = officeAcceptsBCBS;
          if (bio.toLowerCase().includes('blue cross') || bio.toLowerCase().includes('bcbs')) {
            if (bio.toLowerCase().includes('not accept') || bio.toLowerCase().includes('don\'t accept') || bio.toLowerCase().includes('do not accept')) {
              bcbs = "No";
            } else {
              bcbs = "Yes";
            }
          }
          
          // Check for telehealth mention in bio or use office-wide value
          let telehealth = officeTelehealth;
          const bioLower = bio.toLowerCase();
          if (bioLower.includes('telehealth') || bioLower.includes('virtual') || bioLower.includes('online session')) {
            telehealth = "Yes";
            // Check if in-person is also mentioned
            if (bioLower.includes('in person') || bioLower.includes('in-person') || bioLower.includes('office visit')) {
              telehealth = "Both";
            }
          } else if (bioLower.includes('in person only') || bioLower.includes('in-person only')) {
            telehealth = "No";
          }
          
          therapists.push({
            name,
            group: website.group,
            location: officeAddress,
            bio,
            notes: '',
            phone: officePhone,
            email: '', // No emails visible on the page
            url: website.url,
            bcbs,
            emdr,
            telehealth
          });
        } catch (error) {
          console.error(`Error extracting therapist from card:`, error.message);
        }
      });
    }
    
    // If no therapists found, use a more generic approach
    if (therapists.length === 0) {
      console.log("No therapists found with cards, trying alternative selectors");
      
      // Look for all headings that might be therapist names
      const headings = $('h2, h3, h4').filter(function() {
        const text = $(this).text().trim();
        // Filter for headings that look like names with credentials
        return /^[A-Z][a-z]+ [A-Z][a-z]+, [A-Z]+/i.test(text);
      });
      
      console.log(`Found ${headings.length} potential therapist name headings`);
      
      headings.each((i, heading) => {
        try {
          const fullName = $(heading).text().trim();
          let name = fullName;
          
          // Split name from credentials
          const nameParts = fullName.split(',');
          if (nameParts.length > 1) {
            name = nameParts[0].trim();
          }
          
          console.log(`Found therapist: ${name}`);
          
          // Find bio - look in next element
          let bio = '';
          const nextEl = $(heading).next();
          if (nextEl.length > 0) {
            bio = nextEl.text().trim();
          }
          
          // EMDR, BCBS, and telehealth checks
          const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
          let bcbs = officeAcceptsBCBS;
          let telehealth = officeTelehealth;
          
          therapists.push({
            name,
            group: website.group,
            location: officeAddress,
            bio,
            notes: '',
            phone: officePhone,
            email: '',
            url: website.url,
            bcbs,
            emdr,
            telehealth
          });
        } catch (error) {
          console.error(`Error extracting therapist from heading:`, error.message);
        }
      });
    }
    
    return therapists;
  } catch (error) {
    console.error(`Error extracting from Thrive Counseling:`, error.message);
    return [];
  }
}

// Extract therapist info from Anna Thames Counseling
async function extractFromAnnaThamesCounseling(website) {
  try {
    console.log(`Scraping data from Anna Thames Counseling: ${website.url}`);
    
    // Get main page for general office info
    const mainResponse = await axios.get(website.url);
    const main$ = cheerio.load(mainResponse.data);
    
    // Office contact information
    let officeAddress = '';
    let officePhone = '';
    
    // Try to get contact info from footer or contact section
    const footerAddress = main$('.footer-address, .address, .contact-info address').text().trim();
    if (footerAddress) {
      officeAddress = footerAddress;
      console.log(`Found office address from footer: ${officeAddress}`);
    }
    
    const footerPhone = main$('.footer-phone, .phone, a[href^="tel:"]').first().text().trim();
    if (footerPhone) {
      officePhone = footerPhone;
      console.log(`Found office phone from footer: ${officePhone}`);
    } else {
      // Try to extract from href attribute
      const phoneLink = main$('a[href^="tel:"]').first().attr('href');
      if (phoneLink) {
        officePhone = phoneLink.replace('tel:', '');
        console.log(`Found office phone from link: ${officePhone}`);
      }
    }
    
    // If not found on main page, try contact page
    if (!officeAddress || !officePhone) {
      try {
        const contactUrl = `${new URL(website.url).origin}/contact`;
        console.log(`Checking contact page: ${contactUrl}`);
        
        const contactResponse = await axios.get(contactUrl);
        const contact$ = cheerio.load(contactResponse.data);
        
        if (!officeAddress) {
          const contactPageAddress = contact$('.address, address').text().trim();
          if (contactPageAddress) {
            officeAddress = contactPageAddress;
            console.log(`Found office address from contact page: ${officeAddress}`);
          } else {
            // Try regex pattern for address
            const pageText = contact$('body').text();
            const addressMatch = pageText.match(/\d+\s+[\w\s]+(?:Road|Street|Avenue|Lane|Drive|Blvd|Boulevard|Pkwy|Parkway|Rd|St|Ave|Ln|Dr),\s*[\w\s]+,\s*[A-Z]{2}\s*\d{5}/i);
            if (addressMatch) {
              officeAddress = addressMatch[0];
              console.log(`Found office address from contact page text: ${officeAddress}`);
            }
          }
        }
        
        if (!officePhone) {
          const contactPagePhone = contact$('.phone, a[href^="tel:"]').first().text().trim();
          if (contactPagePhone) {
            officePhone = contactPagePhone;
            console.log(`Found office phone from contact page: ${officePhone}`);
          } else {
            // Try to extract from href attribute
            const phoneLink = contact$('a[href^="tel:"]').first().attr('href');
            if (phoneLink) {
              officePhone = phoneLink.replace('tel:', '');
              console.log(`Found office phone from contact page link: ${officePhone}`);
            } else {
              // Try regex pattern for phone
              const pageText = contact$('body').text();
              const phoneMatch = pageText.match(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
              if (phoneMatch) {
                officePhone = phoneMatch[0];
                console.log(`Found office phone from contact page text: ${officePhone}`);
              }
            }
          }
        }
      } catch (contactError) {
        console.error('Error fetching contact page:', contactError.message);
      }
    }
    
    // Check for insurance and telehealth information
    let officeAcceptsBCBS = "Unknown";
    let officeTelehealth = "Unknown";
    
    // Try FAQ or Insurance page
    try {
      const faqUrl = `${new URL(website.url).origin}/faq`;
      console.log(`Checking FAQ page: ${faqUrl}`);
      
      const faqResponse = await axios.get(faqUrl);
      const faq$ = cheerio.load(faqResponse.data);
      
      const faqText = faq$('body').text().toLowerCase();
      
      // Check for BCBS mentions
      if (faqText.includes('blue cross') || faqText.includes('bcbs')) {
        if (faqText.includes('not accept') || faqText.includes('don\'t accept') || faqText.includes('do not accept')) {
          officeAcceptsBCBS = "No";
        } else {
          officeAcceptsBCBS = "Yes";
        }
        console.log(`Found BCBS info from FAQ page: ${officeAcceptsBCBS}`);
      }
      
      // Check for telehealth mentions
      if (faqText.includes('telehealth') || faqText.includes('virtual') || faqText.includes('online session') || faqText.includes('remote session')) {
        officeTelehealth = "Yes";
        // Check if in-person is also mentioned
        if (faqText.includes('in person') || faqText.includes('in-person') || faqText.includes('office')) {
          officeTelehealth = "Both";
        }
        console.log(`Found telehealth info from FAQ page: ${officeTelehealth}`);
      } else if (faqText.includes('in person only') || faqText.includes('in-person only') || faqText.includes('office visits only')) {
        officeTelehealth = "No";
        console.log(`Found telehealth info from FAQ page: ${officeTelehealth}`);
      }
    } catch (faqError) {
      console.error('Error fetching FAQ page:', faqError.message);
      
      // Try insurance or rates page as fallback
      try {
        const insuranceUrl = `${new URL(website.url).origin}/insurance` || `${new URL(website.url).origin}/rates`;
        console.log(`Checking insurance page: ${insuranceUrl}`);
        
        const insuranceResponse = await axios.get(insuranceUrl);
        const insurance$ = cheerio.load(insuranceResponse.data);
        
        const insuranceText = insurance$('body').text().toLowerCase();
        
        // Check for BCBS mentions
        if (insuranceText.includes('blue cross') || insuranceText.includes('bcbs')) {
          if (insuranceText.includes('not accept') || insuranceText.includes('don\'t accept') || insuranceText.includes('do not accept')) {
            officeAcceptsBCBS = "No";
          } else {
            officeAcceptsBCBS = "Yes";
          }
          console.log(`Found BCBS info from insurance page: ${officeAcceptsBCBS}`);
        }
        
        // Check for telehealth mentions
        if (insuranceText.includes('telehealth') || insuranceText.includes('virtual') || insuranceText.includes('online session') || insuranceText.includes('remote session')) {
          officeTelehealth = "Yes";
          // Check if in-person is also mentioned
          if (insuranceText.includes('in person') || insuranceText.includes('in-person') || insuranceText.includes('office')) {
            officeTelehealth = "Both";
          }
          console.log(`Found telehealth info from insurance page: ${officeTelehealth}`);
        } else if (insuranceText.includes('in person only') || insuranceText.includes('in-person only') || insuranceText.includes('office visits only')) {
          officeTelehealth = "No";
          console.log(`Found telehealth info from insurance page: ${officeTelehealth}`);
        }
      } catch (insuranceError) {
        console.error('Error fetching insurance page:', insuranceError.message);
      }
    }
    
    // Find the team/about page
    let therapistsPage = website.url;
    
    // Look for links to team or about page
    const teamLinks = main$('a[href*="about"], a[href*="team"], a[href*="staff"], a[href*="therapist"], a[href*="counselor"]');
    if (teamLinks.length > 0) {
      const teamHref = teamLinks.first().attr('href');
      if (teamHref) {
        therapistsPage = teamHref.startsWith('http') ? teamHref : new URL(teamHref, website.url).toString();
        console.log(`Found team page: ${therapistsPage}`);
      }
    }
    
    // Get therapist page
    const therapistResponse = await axios.get(therapistsPage);
    const therapistPageContent = cheerio.load(therapistResponse.data);
    
    // Find therapist sections
    const therapistSections = therapistPageContent('.sqs-block-content, .staff-section, .team-section, .about-section, .therapists-section');
    
    const therapists = [];
    
    therapistSections.each((i, section) => {
      try {
        // Look for headings which often indicate therapist names
        const nameElement = $(section).find('h2, h3, h4, .staff-name, .therapist-name').first();
        
        if (nameElement.length) {
          const name = nameElement.text().trim();
          
          // Only proceed if name seems valid (not just section titles)
          if (name && !name.toLowerCase().includes('our team') && !name.toLowerCase().includes('about us')) {
            console.log(`Found potential therapist: ${name}`);
            
            // Find bio - could be in paragraphs after the name
            let bio = '';
            const bioElements = $(section).find('p');
            bioElements.each((j, el) => {
              // Skip paragraphs that look like contact info
              const text = $(el).text().trim();
              if (text && !text.match(/^(email|phone|tel):/i) && !text.match(/^\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$/)) {
                bio += (bio ? "\n\n" : "") + text;
              }
            });
            
            // If no structured bio found, use all text except the name
            if (!bio) {
              bio = $(section).text().replace(name, '').trim();
            }
            
            // Extract email
            let email = '';
            const emailLink = $(section).find('a[href^="mailto:"]');
            if (emailLink.length) {
              email = emailLink.attr('href').replace('mailto:', '');
              console.log(`  Found email: ${email}`);
            } else {
              // Try to find email pattern in text
              const emailMatch = bio.match(/[\w.-]+@[\w.-]+\.\w+/);
              if (emailMatch) {
                email = emailMatch[0];
                console.log(`  Found email from text: ${email}`);
              }
            }
            
            // Extract phone number
            let phone = officePhone; // Default to office phone
            const phoneLink = $(section).find('a[href^="tel:"]');
            if (phoneLink.length) {
              phone = phoneLink.attr('href').replace('tel:', '');
              console.log(`  Found phone: ${phone}`);
            } else {
              // Try to find phone pattern in text
              const phoneMatch = bio.match(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
              if (phoneMatch) {
                phone = phoneMatch[0];
                console.log(`  Found phone from text: ${phone}`);
              }
            }
            
            // Check for EMDR mention in bio
            const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
            console.log(`  EMDR: ${emdr}`);
            
            // Check for BCBS mention in bio or use office-wide value
            let bcbs = officeAcceptsBCBS;
            if (bio.toLowerCase().includes('blue cross') || bio.toLowerCase().includes('bcbs')) {
              if (bio.toLowerCase().includes('not accept') || bio.toLowerCase().includes('don\'t accept') || bio.toLowerCase().includes('do not accept')) {
                bcbs = "No";
              } else {
                bcbs = "Yes";
              }
            }
            
            // Check for telehealth mention in bio or use office-wide value
            let telehealth = officeTelehealth;
            const bioLower = bio.toLowerCase();
            if (bioLower.includes('telehealth') || bioLower.includes('virtual') || bioLower.includes('online')) {
              telehealth = "Yes";
              // Check if in-person is also mentioned
              if (bioLower.includes('in person') || bioLower.includes('in-person') || bioLower.includes('office')) {
                telehealth = "Both";
              }
            } else if (bioLower.includes('in person only') || bioLower.includes('in-person only') || bioLower.includes('office only')) {
              telehealth = "No";
            }
            
            therapists.push({
              name,
              group: website.group,
              location: officeAddress || "Monroe, NC area",
              bio,
              notes: '',
              phone,
              email,
              url: therapistsPage,
              bcbs,
              emdr,
              telehealth
            });
          }
        }
      } catch (sectionError) {
        console.error(`Error extracting from section:`, sectionError.message);
      }
    });
    
    if (therapists.length === 0) {
      console.log('No therapists found using headings approach, trying alternative method');
      
      // Alternative approach - look for specific content blocks or divs
      const contentBlocks = $('.team-member, .staff-member, .bio-block, .therapist-card');
      
      if (contentBlocks.length > 0) {
        console.log(`Found ${contentBlocks.length} potential therapist blocks`);
        
        contentBlocks.each((i, block) => {
          try {
            const name = $(block).find('h2, h3, h4, .name, .title').first().text().trim();
            if (!name) return;
            
            console.log(`Found therapist from block: ${name}`);
            
            const bio = $(block).find('p, .bio, .description').text().trim();
            
            // Extract email
            let email = '';
            const emailLink = $(block).find('a[href^="mailto:"]');
            if (emailLink.length) {
              email = emailLink.attr('href').replace('mailto:', '');
              console.log(`  Found email: ${email}`);
            } else {
              // Try to find email pattern in text
              const emailMatch = bio.match(/[\w.-]+@[\w.-]+\.\w+/);
              if (emailMatch) {
                email = emailMatch[0];
                console.log(`  Found email from text: ${email}`);
              }
            }
            
            // Extract phone number
            let phone = officePhone; // Default to office phone
            const phoneLink = $(block).find('a[href^="tel:"]');
            if (phoneLink.length) {
              phone = phoneLink.attr('href').replace('tel:', '');
              console.log(`  Found phone: ${phone}`);
            } else {
              // Try to find phone pattern in text
              const phoneMatch = bio.match(/(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
              if (phoneMatch) {
                phone = phoneMatch[0];
                console.log(`  Found phone from text: ${phone}`);
              }
            }
            
            // Check for EMDR mention in bio
            const emdr = bio.toLowerCase().includes('emdr') ? "Yes" : "No";
            console.log(`  EMDR: ${emdr}`);
            
            // Check for BCBS mention in bio or use office-wide value
            let bcbs = officeAcceptsBCBS;
            if (bio.toLowerCase().includes('blue cross') || bio.toLowerCase().includes('bcbs')) {
              if (bio.toLowerCase().includes('not accept') || bio.toLowerCase().includes('don\'t accept') || bio.toLowerCase().includes('do not accept')) {
                bcbs = "No";
              } else {
                bcbs = "Yes";
              }
            }
            
            // Check for telehealth mention in bio or use office-wide value
            let telehealth = officeTelehealth;
            const bioLower = bio.toLowerCase();
            if (bioLower.includes('telehealth') || bioLower.includes('virtual') || bioLower.includes('online')) {
              telehealth = "Yes";
              // Check if in-person is also mentioned
              if (bioLower.includes('in person') || bioLower.includes('in-person') || bioLower.includes('office')) {
                telehealth = "Both";
              }
            } else if (bioLower.includes('in person only') || bioLower.includes('in-person only') || bioLower.includes('office only')) {
              telehealth = "No";
            }
            
            therapists.push({
              name,
              group: website.group,
              location: officeAddress || "Monroe, NC area",
              bio,
              notes: '',
              phone,
              email,
              url: therapistsPage,
              bcbs,
              emdr,
              telehealth
            });
          } catch (blockError) {
            console.error(`Error extracting from content block:`, blockError.message);
          }
        });
      }
    }
    
    if (therapists.length === 0) {
      console.log('No therapists found, adding Anna Thames as default');
      
      // If no therapists found, assume it's a solo practice
      therapists.push({
        name: "Anna Thames",
        group: website.group,
        location: officeAddress || "Monroe, NC area",
        bio: main$('body').text().substring(0, 500) + '...',
        notes: 'Added as default for solo practice',
        phone: officePhone,
        email: '',
        url: website.url,
        bcbs: officeAcceptsBCBS,
        emdr: main$('body').text().toLowerCase().includes('emdr') ? "Yes" : "No",
        telehealth: officeTelehealth
      });
    }
    
    return therapists;
  } catch (error) {
    console.error(`Error extracting from Anna Thames Counseling:`, error.message);
    return [];
  }
}

/**
 * Import therapist data to Notion database
 * @param {Array} therapists - Array of therapist objects
 * @returns {Promise<number>} - Number of therapists imported
 */
async function importTherapistsToNotion(therapists) {
  if (!process.env.NOTION_TOKEN || !process.env.THERAPIST_DB_ID) {
    throw new Error('Missing required environment variables: NOTION_TOKEN or THERAPIST_DB_ID');
  }
  
  const notion = new Client({ auth: process.env.NOTION_TOKEN });
  
  // First, get existing therapists to avoid duplicates
  console.log('Checking for existing therapists in the database...');
  const existingTherapists = await getExistingTherapists(notion);
  const existingNames = existingTherapists.map(t => t.properties.Name.title[0]?.plain_text.toLowerCase().trim());
  
  console.log(`Found ${existingNames.length} existing therapists in the database.`);
  
  let importedCount = 0;
  let skippedCount = 0;
  
  for (const therapist of therapists) {
    // Check if therapist already exists by name
    if (existingNames.includes(therapist.name.toLowerCase().trim())) {
      console.log(`Skipping duplicate therapist: ${therapist.name}`);
      skippedCount++;
      continue;
    }
    
    try {
      const properties = createTherapistEntry(therapist);
      
      await notion.pages.create({
        parent: {
          database_id: process.env.THERAPIST_DB_ID
        },
        properties
      });
      
      console.log(`Imported therapist: ${therapist.name} from ${therapist.group}`);
      importedCount++;
      
      // Add a small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      console.error(`Error importing therapist ${therapist.name}:`, error.message);
    }
  }
  
  console.log(`Import completed: ${importedCount} imported, ${skippedCount} skipped (duplicates)`);
  return importedCount;
}

/**
 * Get existing therapists from the Notion database
 * @param {Client} notion - Notion client instance
 * @returns {Promise<Array>} - Array of existing therapist pages
 */
async function getExistingTherapists(notion) {
  try {
    const response = await notion.databases.query({
      database_id: process.env.THERAPIST_DB_ID,
      page_size: 100, // Adjust as needed
    });
    
    return response.results;
  } catch (error) {
    console.error('Error fetching existing therapists:', error.message);
    return [];
  }
}

/**
 * Main function to extract therapists from all websites and import to Notion
 */
async function extractAndImportTherapists() {
  const websites = [
    { name: 'Reaching Resolution', url: 'https://www.reachingresolution.net/meet-the-team', group: 'Reaching Resolution' },
    { name: 'Neuro Connection', url: 'https://neuronnection.com/profile/', group: 'NeuroConnection' },
    { name: 'Thrive Counseling', url: 'https://www.thrivecounselingnc.com/team', group: 'Thrive Counseling' },
    { name: 'Anna Thames Counseling', url: 'https://www.annathamescounseling.com/team', group: 'Anna Thames Counseling' },
  ];

  let allTherapists = [];
  let totalFound = 0;

  // Extract therapists from each website
  for (const website of websites) {
    console.log(`\n=== Processing ${website.name} ===`);
    // Verify group is set or fallback to website name
    const group = website.group || website.name;
    
    let therapists = [];
    
    try {
      switch(website.name) {
        case 'Reaching Resolution':
          therapists = await extractFromReachingResolution(website);
          break;
        case 'Neuro Connection': 
          therapists = await extractFromNeuroConnection(website);
          break;
        case 'Thrive Counseling':
          therapists = await extractFromThriveCounseling(website);
          break;
        case 'Anna Thames Counseling':
          therapists = await extractFromAnnaThamesCounseling(website);
          break;
        default:
          console.log(`No extraction function for ${website.name}`);
      }
      
      // Verify each therapist has the correct group
      therapists = therapists.map(therapist => {
        if (!therapist.group) {
          console.warn(`Warning: Therapist ${therapist.name} has no group. Setting to ${group}`);
          therapist.group = group;
        } else if (therapist.group !== group) {
          console.warn(`Warning: Therapist ${therapist.name} has inconsistent group. Expected ${group}, found ${therapist.group}`);
          therapist.group = group;
        }
        
        // Log each therapist with their group for debugging
        console.log(`Processed: ${therapist.name} (Group: ${therapist.group})`);
        
        return therapist;
      });
      
      allTherapists = [...allTherapists, ...therapists];
      totalFound += therapists.length;
      console.log(`Found ${therapists.length} therapists from ${website.name}`);
    } catch (error) {
      console.error(`Error processing ${website.name}:`, error.message);
    }
  }

  console.log(`\n=== Total therapists found: ${totalFound} ===`);
  console.log(`=== Group distribution: ===`);
  const groupCounts = {};
  allTherapists.forEach(therapist => {
    groupCounts[therapist.group] = (groupCounts[therapist.group] || 0) + 1;
  });
  
  Object.entries(groupCounts).forEach(([group, count]) => {
    console.log(`- ${group}: ${count} therapists`);
  });
  
  // Import to Notion if any therapists were found
  if (allTherapists.length > 0) {
    try {
      console.log(`\nImporting ${allTherapists.length} therapists to Notion...`);
      const importedCount = await importTherapistsToNotion(allTherapists);
      console.log(`Successfully imported ${importedCount} new therapists to Notion database.`);
    } catch (error) {
      console.error('Error during import to Notion:', error.message);
    }
  } else {
    console.log('No therapists found to import.');
  }
}

// Run the main function
extractAndImportTherapists(); 