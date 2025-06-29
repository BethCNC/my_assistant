import dotenv from 'dotenv';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

// Convert exec to return a Promise
const execAsync = promisify(exec);

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function runScript(scriptName: string): Promise<void> {
  console.log(`\n====== Running ${scriptName} ======\n`);
  try {
    // Use ts-node to run the TypeScript files directly
    const command = `npx ts-node scripts/${scriptName}.ts`;
    const { stdout, stderr } = await execAsync(command);
    
    if (stdout) {
      console.log(stdout);
    }
    
    if (stderr) {
      console.error(stderr);
    }
    
    console.log(`\n====== Completed ${scriptName} ======\n`);
  } catch (error) {
    console.error(`Error running ${scriptName}:`, error);
    process.exit(1);
  }
}

async function importAllData() {
  try {
    // Order matters here - we import in a sequence that respects foreign key relationships
    
    // First, import medical providers (no dependencies)
    await runScript('import-medical-team');
    
    // Next, import diagnoses (may depend on providers)
    await runScript('import-diagnoses');
    
    // Then, import symptoms (no dependencies, but relations will reference diagnoses)
    await runScript('import-symptoms');
    
    // Import Epic FHIR data (includes providers, conditions, and medical events)
    await runScript('import-from-epic');
    
    // Finally, import medical events (depends on providers, diagnoses, and potentially symptoms)
    await runScript('import-medical-calendar');
    
    console.log('\n====== All imports completed successfully! ======\n');
  } catch (error) {
    console.error('Error during import process:', error);
    process.exit(1);
  }
}

// Install required packages if they're not already installed
async function installDependencies() {
  try {
    console.log('Checking for required dependencies...');
    await execAsync('npm install --no-save ts-node dotenv axios');
    console.log('Dependencies installed/verified.');
  } catch (error) {
    console.error('Error installing dependencies:', error);
    process.exit(1);
  }
}

// Run the entire import process
async function main() {
  await installDependencies();
  await importAllData();
}

main().catch(console.error); 