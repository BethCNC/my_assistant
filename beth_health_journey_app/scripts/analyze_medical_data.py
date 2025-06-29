import os
import mimetypes
from pathlib import Path
import json
import time
import re
import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("medical_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# OpenAI
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

# PDF
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# DOCX
try:
    import docx
except ImportError:
    docx = None

# RTF
try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None

# HTML
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Supported file extensions
EXTENSIONS = {
    '.pdf': 'PDF',
    '.txt': 'Text',
    '.csv': 'CSV',
    '.html': 'HTML',
    '.htm': 'HTML',
    '.rtf': 'RTF',
    '.docx': 'DOCX',
    '.json': 'JSON',
}

DATA_ROOT = Path('data')
OUTPUT_DIR = Path('processed-data')

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

def detect_file_type(filepath):
    ext = filepath.suffix.lower()
    return EXTENSIONS.get(ext, 'Unknown')


def extract_text(filepath, ftype):
    try:
        if ftype == 'PDF':
            if not pdfplumber:
                return '[pdfplumber not installed]'
            with pdfplumber.open(filepath) as pdf:
                return '\n'.join(page.extract_text() or '' for page in pdf.pages)
        elif ftype == 'Text':
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ftype == 'CSV':
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ftype == 'HTML':
            if not BeautifulSoup:
                return '[BeautifulSoup not installed]'
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                return soup.get_text(separator='\n')
        elif ftype == 'RTF':
            if not rtf_to_text:
                return '[striprtf not installed]'
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                return rtf_to_text(f.read())
        elif ftype == 'DOCX':
            if not docx:
                return '[python-docx not installed]'
            doc = docx.Document(filepath)
            return '\n'.join([p.text for p in doc.paragraphs])
        elif ftype == 'JSON':
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            return '[Unsupported file type]'
    except Exception as e:
        return f'[Error extracting text: {e}]'


def analyze_with_openai(text, filepath):
    """Use OpenAI to analyze medical document text and extract structured information"""
    
    if not OpenAI:
        logger.error("OpenAI package not installed")
        return {"error": "OpenAI package not installed"}
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables")
        return {"error": "OPENAI_API_KEY not found in environment variables"}
    
    # Truncate text if it's too long (GPT-4 has token limits)
    max_tokens = 16000  # Leave room for the response
    if len(text) > max_tokens * 4:  # Rough estimate of tokens
        logger.warning(f"Text is too long, truncating: {filepath}")
        text = text[:max_tokens * 4]
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Formulate the prompt with specific instructions for medical data extraction
        prompt = f"""
        You are a medical data analyzer specialized in healthcare records. Analyze the following medical document:
        
        {text}
        
        Extract and structure the following information:
        1. Document Type: Identify if this is a lab result, doctor's note, medical summary, etc.
        2. Date: Identify the date(s) mentioned (appointment date, test date, etc.)
        3. Medical Provider: Name and specialty of the healthcare provider if mentioned
        4. Facility: Hospital, clinic, or lab name
        5. Patient Information: Any patient identifiers (but maintain privacy)
        6. Diagnoses: Any diagnosed conditions mentioned
        7. Symptoms: Any symptoms reported 
        8. Treatments: Any medications, procedures, or therapies mentioned
        9. Lab Results: Extract test names, values, and reference ranges
        10. Key Findings: Summarize the most important medical information
        11. Follow-up: Any recommended follow-up actions
        
        Format the response as JSON with appropriate fields. Use null for missing information.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical data extraction assistant. Your task is to extract structured information from medical documents and format it as clean JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,  # Deterministic output
            response_format={"type": "json_object"}  # Ensure JSON format
        )
        
        # Extract and parse the JSON response
        analysis_result = json.loads(response.choices[0].message.content)
        logger.info(f"Successfully analyzed {filepath}")
        
        return analysis_result
    
    except Exception as e:
        logger.error(f"Error analyzing with OpenAI: {e}")
        return {"error": str(e)}


def process_file(filepath):
    """Process a single file: extract text, analyze with AI, and save results"""
    ftype = detect_file_type(filepath)
    logger.info(f"Processing {filepath} | {ftype}")
    
    # Extract text from file
    text = extract_text(filepath, ftype)
    if not text or text.startswith('[Error'):
        logger.error(f"Failed to extract text from {filepath}: {text}")
        return None
    
    # Analyze with OpenAI
    analysis_result = analyze_with_openai(text, filepath)
    
    # Create output filename based on source file
    rel_path = filepath.relative_to(DATA_ROOT) if filepath.is_relative_to(DATA_ROOT) else filepath.name
    output_file = OUTPUT_DIR / f"{rel_path.stem}_analysis.json"
    
    # Create parent directories if they don't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save raw text for reference
    text_file = OUTPUT_DIR / f"{rel_path.stem}_raw.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Save analysis results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2)
    
    logger.info(f"Saved analysis to {output_file}")
    return analysis_result


def scan_data_dir(root):
    """Scan the data directory and process all supported files"""
    results = []
    
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            ftype = detect_file_type(fpath)
            
            if ftype != 'Unknown':
                result = process_file(fpath)
                if result:
                    results.append({
                        "file": str(fpath),
                        "analysis": result
                    })
            else:
                logger.info(f"Skipping unsupported file: {fpath}")
    
    # Save the combined results
    combined_file = OUTPUT_DIR / "combined_analysis.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved combined analysis to {combined_file}")
    return results


def structure_notion_import(combined_results):
    """Structure the analyzed data for Notion import"""
    
    # Map our analysis to Notion databases
    medical_calendar = []
    symptoms = []
    medical_team = []
    medications = []
    
    for result in combined_results:
        analysis = result.get("analysis", {})
        
        # Skip entries with errors
        if "error" in analysis:
            continue
        
        # Create a Medical Calendar entry
        if analysis.get("Date"):
            try:
                # Try to parse the date
                date = parse_date(analysis.get("Date"))
                
                event_type = map_to_event_type(analysis.get("Document Type", ""))
                
                calendar_entry = {
                    "title": generate_title(analysis),
                    "date": date,
                    "type": event_type,
                    "doctor": analysis.get("Medical Provider"),
                    "facility": analysis.get("Facility"),
                    "diagnoses": analysis.get("Diagnoses"),
                    "summary": analysis.get("Key Findings"),
                    "follow_up": analysis.get("Follow-up"),
                    "source_file": result.get("file"),
                }
                medical_calendar.append(calendar_entry)
            except Exception as e:
                logger.error(f"Error creating calendar entry: {e}")
        
        # Extract symptoms
        if analysis.get("Symptoms"):
            symptoms_list = parse_list_field(analysis.get("Symptoms"))
            for symptom in symptoms_list:
                symptoms.append({
                    "name": symptom,
                    "related_diagnoses": analysis.get("Diagnoses"),
                    "date_recorded": analysis.get("Date"),
                    "source_file": result.get("file"),
                })
        
        # Extract healthcare providers
        if analysis.get("Medical Provider"):
            provider = analysis.get("Medical Provider")
            specialty = extract_specialty(provider)
            medical_team.append({
                "name": clean_provider_name(provider),
                "specialty": specialty,
                "facility": analysis.get("Facility"),
                "first_visit": analysis.get("Date"),
                "source_file": result.get("file"),
            })
        
        # Extract medications
        if analysis.get("Treatments"):
            treatments = parse_list_field(analysis.get("Treatments"))
            for treatment in treatments:
                if is_medication(treatment):
                    medications.append({
                        "name": extract_medication_name(treatment),
                        "dosage": extract_dosage(treatment),
                        "related_diagnoses": analysis.get("Diagnoses"),
                        "prescribed_date": analysis.get("Date"),
                        "prescribed_by": analysis.get("Medical Provider"),
                        "source_file": result.get("file"),
                    })
    
    # Save structured data for Notion import
    notion_data = {
        "medical_calendar": medical_calendar,
        "symptoms": symptoms,
        "medical_team": medical_team,
        "medications": medications,
    }
    
    notion_file = OUTPUT_DIR / "notion_import_data.json"
    with open(notion_file, 'w', encoding='utf-8') as f:
        json.dump(notion_data, f, indent=2)
    
    logger.info(f"Saved Notion import data to {notion_file}")
    return notion_data


# Helper functions for structuring Notion import data
def parse_date(date_str):
    """Parse date string to ISO format"""
    if not date_str:
        return None
    
    # Try different date formats
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).isoformat()
        except ValueError:
            pass
    
    # If no format matches, try to extract date with regex
    date_pattern = r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})'
    match = re.search(date_pattern, date_str)
    if match:
        month, day, year = match.groups()
        if len(year) == 2:
            year = f"20{year}" if int(year) < 50 else f"19{year}"
        
        try:
            return datetime.datetime(int(year), int(month), int(day)).isoformat()
        except ValueError:
            pass
    
    # If all else fails, return the original string
    return date_str


def map_to_event_type(document_type):
    """Map document type to Notion event type"""
    document_type = document_type.lower()
    
    if "lab" in document_type or "test" in document_type:
        return "Lab Result"
    elif "note" in document_type or "visit" in document_type or "appointment" in document_type:
        return "Doctor's Notes - Appt Notes"
    elif "surgery" in document_type or "procedure" in document_type:
        return "Surgery"
    elif "discharge" in document_type:
        return "Hospital Stay"
    elif "imaging" in document_type or "x-ray" in document_type or "mri" in document_type:
        return "Imaging"
    else:
        return "Other"


def generate_title(analysis):
    """Generate a standardized title for the Medical Calendar entry"""
    doc_type = analysis.get("Document Type", "")
    date = analysis.get("Date", "")
    provider = analysis.get("Medical Provider", "")
    
    if "lab" in doc_type.lower() or "test" in doc_type.lower():
        # For lab results: "[Test Name] - [Date]"
        test_name = extract_test_name(analysis)
        if test_name:
            return f"{test_name} - {date}"
        else:
            return f"Lab Results - {date}"
    elif any(term in doc_type.lower() for term in ["visit", "appointment", "note"]):
        # For appointments: "[Specialty Type] Visit - [Date]"
        specialty = extract_specialty(provider)
        if specialty:
            return f"{specialty} Visit - {date}"
        else:
            return f"Doctor Visit - {date}"
    else:
        # Default format
        return f"{doc_type} - {date}"


def extract_test_name(analysis):
    """Extract the primary test name from lab results"""
    if not analysis.get("Lab Results"):
        return None
    
    lab_results = analysis.get("Lab Results")
    if isinstance(lab_results, str):
        # Try to extract the first test name
        matches = re.findall(r'([A-Za-z\s]+):', lab_results)
        if matches:
            return matches[0].strip()
    
    return None


def extract_specialty(provider):
    """Extract specialty from provider string"""
    if not provider:
        return None
    
    # Common specialties
    specialties = [
        "Primary Care", "Family Medicine", "Internal Medicine", 
        "Cardiology", "Neurology", "Gastroenterology", "Endocrinology",
        "Dermatology", "Ophthalmology", "ENT", "Orthopedics", "Oncology",
        "Rheumatology", "Pulmonology", "Nephrology", "Psychiatry",
        "Gynecology", "Urology"
    ]
    
    for specialty in specialties:
        if specialty.lower() in provider.lower():
            return specialty
    
    # Try to extract "Dr. X, Specialty"
    match = re.search(r'Dr\.\s+[^,]+,\s+([^,]+)', provider)
    if match:
        return match.group(1).strip()
    
    return "General Practitioner"


def clean_provider_name(provider):
    """Clean the provider name"""
    if not provider:
        return None
    
    # Remove any specialty information after a comma
    match = re.match(r'([^,]+)', provider)
    if match:
        return match.group(1).strip()
    
    return provider


def parse_list_field(field):
    """Parse a field that might contain a list of items"""
    if not field:
        return []
    
    if isinstance(field, list):
        return field
    
    if isinstance(field, str):
        # Split by common delimiters
        items = re.split(r'[,;]\s*', field)
        return [item.strip() for item in items if item.strip()]
    
    return []


def is_medication(treatment):
    """Determine if a treatment is a medication"""
    med_indicators = [
        "mg", "mcg", "tablet", "capsule", "pill", "injection",
        "daily", "twice", "weekly", "dose", "prescription", "rx"
    ]
    
    treatment_lower = treatment.lower()
    return any(indicator in treatment_lower for indicator in med_indicators)


def extract_medication_name(medication):
    """Extract the medication name from the treatment string"""
    # Try to extract just the name without dosage
    match = re.match(r'^([A-Za-z\s\-]+)', medication)
    if match:
        return match.group(1).strip()
    
    return medication


def extract_dosage(medication):
    """Extract the dosage from a medication string"""
    # Look for common dosage patterns
    dosage_patterns = [
        r'(\d+\s*(?:mg|mcg|g|ml))',
        r'(\d+\s*(?:tablet|capsule|pill)s?)',
    ]
    
    for pattern in dosage_patterns:
        match = re.search(pattern, medication, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


if __name__ == "__main__":
    logger.info("Starting medical data analysis")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY") and OpenAI:
        logger.warning("OPENAI_API_KEY not found. Please set it in .env file.")
    
    # Process all files
    results = scan_data_dir(DATA_ROOT)
    
    # Structure data for Notion import
    notion_data = structure_notion_import(results)
    
    logger.info("Analysis complete. Results saved to the processed-data directory.") 