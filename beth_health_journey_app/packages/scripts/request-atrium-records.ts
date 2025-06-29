import path from 'path';
import fs from 'fs';
import readline from 'readline';
import { exec } from 'child_process';
import dayjs from 'dayjs';

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to prompt for user input
function prompt(question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

// Create directory if it doesn't exist
function ensureDirectoryExists(directoryPath: string) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
  }
}

/**
 * Generate a health record request template
 */
async function generateHealthRecordRequest() {
  console.log('===== Atrium Health Record Request Generator =====');
  console.log('This script generates a template letter to request your complete health records.\n');
  
  // Create directory for request letter
  const requestDir = path.join(process.cwd(), 'data/atrium-request');
  ensureDirectoryExists(requestDir);
  
  // Collect information for the request
  console.log('Please provide the following information for your request:');
  
  const fullName = await prompt('Your full name: ');
  const dob = await prompt('Your date of birth (MM/DD/YYYY): ');
  const address = await prompt('Your mailing address: ');
  const phone = await prompt('Your phone number: ');
  const email = await prompt('Your email address: ');
  
  // Date range 
  const startDate = await prompt('Record start date (MM/DD/YYYY or "all" for all records): ');
  const endDate = await prompt('Record end date (MM/DD/YYYY or "present" for current date): ');
  
  // Format dates
  const formattedStartDate = startDate.toLowerCase() === 'all' 
    ? 'all available records' 
    : dayjs(startDate, 'MM/DD/YYYY').format('MMMM D, YYYY');
  
  const formattedEndDate = endDate.toLowerCase() === 'present' 
    ? dayjs().format('MMMM D, YYYY') 
    : dayjs(endDate, 'MM/DD/YYYY').format('MMMM D, YYYY');
  
  // Request types
  const requestTypes = [
    'Complete Medical Record',
    'Lab Results',
    'Diagnosis/Problem List',
    'Medication List',
    'Appointment History',
    'Radiology Reports',
    'Clinical Notes'
  ];
  
  let selectedTypes: string[] = [];
  
  console.log('\nWhich types of records would you like to request?');
  for (let i = 0; i < requestTypes.length; i++) {
    const includeType = await prompt(`Include ${requestTypes[i]}? (y/n): `);
    if (includeType.toLowerCase() === 'y') {
      selectedTypes.push(requestTypes[i]);
    }
  }
  
  // Format
  console.log('\nPreferred format:');
  const format = await prompt('Format (electronic/paper): ');
  
  // Generate the letter 
  const today = dayjs().format('MMMM D, YYYY');
  
  const letterContent = `${today}

Atrium Health
Medical Records Department
PO Box 32861
Charlotte, NC 28232

RE: Medical Records Request for ${fullName}

To Whom It May Concern:

I am writing to request a copy of my medical records pursuant to the Health Insurance Portability and Accountability Act (HIPAA) and the 21st Century Cures Act.

Patient Information:
- Full Name: ${fullName}
- Date of Birth: ${dob}
- Address: ${address}
- Phone: ${phone}
- Email: ${email}

Records Requested:
${selectedTypes.map(type => `- ${type}`).join('\n')}

For the period from ${formattedStartDate} to ${formattedEndDate}.

I would prefer to receive these records in ${format} format.

Under HIPAA (45 CFR 164.524), I understand that I have the right to access my protected health information in the designated record set. If for any reason any portion of my request cannot be fulfilled, please provide a written explanation of the reasons.

Please process this request within the timeframe mandated by federal and state law. If fees will exceed $25, please notify me before processing this request.

Thank you for your assistance with this matter.

Sincerely,

${fullName}

---

NOTES FOR PATIENT (not part of the letter):
1. Print, sign, and date this letter.
2. Include a copy of your photo ID with the request.
3. You can submit this via the MyChart portal, fax, mail, or in person.
4. MyChart is typically the fastest method for receiving electronic records.
5. Atrium Health contact: 704-667-9405

You may also be able to make this request directly through your MyChart account by:
1. Log in to MyChart
2. Navigate to "Menu" or "Health" 
3. Look for "Medical Records Request" or "Download My Record"
`;

  // Save the letter to a file
  const letterFilePath = path.join(requestDir, 'atrium_records_request.txt');
  fs.writeFileSync(letterFilePath, letterContent);
  
  console.log(`\nLetter has been generated and saved to: ${letterFilePath}`);
  
  // Offer to open the file
  const openFile = await prompt('\nWould you like to open the file now? (y/n): ');
  
  if (openFile.toLowerCase() === 'y') {
    // Attempt to open the file with the default text editor
    try {
      // Different open commands based on platform
      const platform = process.platform;
      let openCommand = '';
      
      if (platform === 'win32') {
        openCommand = `start "" "${letterFilePath}"`;
      } else if (platform === 'darwin') {
        openCommand = `open "${letterFilePath}"`;
      } else {
        openCommand = `xdg-open "${letterFilePath}"`;
      }
      
      exec(openCommand, (error) => {
        if (error) {
          console.error(`Error opening file: ${error.message}`);
          console.log(`You can find the file at: ${letterFilePath}`);
        }
      });
    } catch (error) {
      console.error('Error opening file:', error);
      console.log(`You can find the file at: ${letterFilePath}`);
    }
  }
  
  console.log('\nNext Steps:');
  console.log('1. Review, print, and sign the letter');
  console.log('2. Include a copy of your photo ID');
  console.log('3. Submit through MyChart, fax, mail, or in person');
  console.log('4. Some records may be available immediately through "Share My Record" in MyChart');
  
  rl.close();
}

// Run the script
try {
  generateHealthRecordRequest();
} catch (error: any) {
  console.error('Error:', error?.message || 'Unknown error');
  rl.close();
  process.exit(1);
} 