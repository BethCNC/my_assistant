#!/usr/bin/env python
import os
from pathlib import Path
import logging
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Add project root to path

from src.extraction.factory import get_extractor
from src.processing.factory import process_document


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def test_processing_pipeline(file_path, logger):
    """Test the extraction and processing pipeline for a given file path."""
    logger.info(f"Testing extraction and processing for: {file_path}")
    
    # Step 1: Extract data using the appropriate extractor
    extractor = get_extractor(file_path)
    
    if not extractor:
        logger.error(f"No suitable extractor found for {file_path}")
        return
    
    try:
        # Extract data from the file
        extracted_data = extractor.process_file(file_path)
        logger.info(f"Extraction completed for {file_path}")
        
        # Step 2: Process the extracted data
        processed_data = process_document(extracted_data)
        logger.info(f"Processing completed for {file_path}")
        
        # Print some information about the processed data
        document_type = processed_data.get("metadata", {}).get("document_type", "unknown")
        logger.info(f"Detected document type: {document_type}")
        
        # Print extracted dates
        if "normalized_dates" in processed_data and processed_data["normalized_dates"]:
            logger.info(f"Normalized dates: {processed_data['normalized_dates']}")
        
        # Display lab results if present
        if "lab_results" in processed_data and processed_data["lab_results"]:
            logger.info(f"Found {len(processed_data['lab_results'])} lab results")
            for lab_result in processed_data["lab_results"][:5]:  # Show first 5 only
                logger.info(f"  - {lab_result['test_name']}: {lab_result['value']} {lab_result['unit']}")
        
        # Display medications if present
        if "medical_entities" in processed_data and "medications" in processed_data["medical_entities"]:
            medications = processed_data["medical_entities"]["medications"]
            if medications:
                logger.info(f"Found {len(medications)} medications")
                for med in medications[:5]:  # Show first 5 only
                    logger.info(f"  - {med['name']}: {med['dosage']} {med['unit']}")
        
        # Display condition categories if present
        if "condition_categories" in processed_data:
            for category, terms in processed_data["condition_categories"].items():
                if terms:
                    logger.info(f"Found {len(terms)} terms related to {category}")
                    logger.info(f"  - {', '.join(terms[:5])}")  # Show first 5 only
        
        # Save processed data to a JSON file for inspection
        output_dir = Path("processed_data")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{Path(file_path).stem}_processed.json"
        with open(output_file, 'w') as f:
            # Handle non-serializable types
            json_data = {}
            for key, value in processed_data.items():
                try:
                    # Test if value is JSON serializable
                    json.dumps(value)
                    json_data[key] = value
                except (TypeError, OverflowError):
                    # If not serializable, convert to string representation
                    json_data[key] = str(value)
            
            json.dump(json_data, f, indent=2)
        
        logger.info(f"Processed data saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def test_with_sample_files():
    """Test with available sample files in the samples directory."""
    logger = setup_logging()
    
    # Create samples directory if it doesn't exist
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)
    
    # Check if we have sample files
    sample_files = list(samples_dir.glob("*.*"))
    
    if not sample_files:
        # Create some sample files for testing
        logger.info("No sample files found. Creating sample files for testing...")
        create_sample_files(samples_dir)
        sample_files = list(samples_dir.glob("*.*"))
    
    # Process each sample file
    for file_path in sample_files:
        test_processing_pipeline(file_path, logger)


def create_sample_files(samples_dir):
    """Create sample medical files for testing."""
    # Sample lab result
    lab_result = """
    LABORATORY REPORT
    Date: 2023-06-15
    Patient: John Doe
    
    COMPLETE BLOOD COUNT
    WBC: 7.8 10^3/uL (Reference Range: 4.5-11.0)
    RBC: 4.9 10^6/uL (Reference Range: 4.5-5.9)
    Hemoglobin: 14.2 g/dL (Reference Range: 13.5-17.5)
    Hematocrit: 42% (Reference Range: 41-50)
    Platelets: 250 10^3/uL (Reference Range: 150-400)
    
    BASIC METABOLIC PANEL
    Glucose: 95 mg/dL (Reference Range: 70-99)
    BUN: 15 mg/dL (Reference Range: 7-20)
    Creatinine: 0.9 mg/dL (Reference Range: 0.6-1.2)
    Sodium: 140 mEq/L (Reference Range: 135-145)
    Potassium: 4.0 mEq/L (Reference Range: 3.5-5.0)
    Chloride: 102 mEq/L (Reference Range: 98-107)
    CO2: 24 mEq/L (Reference Range: 23-29)
    Calcium: 9.5 mg/dL (Reference Range: 8.5-10.5)
    
    THYROID PANEL
    TSH: 2.5 uIU/mL (Reference Range: 0.4-4.0)
    Free T4: 1.2 ng/dL (Reference Range: 0.8-1.8)
    
    INFLAMMATORY MARKERS
    CRP: 1.2 mg/L (Reference Range: <3.0)
    ESR: 10 mm/hr (Reference Range: 0-15)
    
    CONNECTIVE TISSUE PANEL
    ANA: Negative (Reference Range: Negative)
    Rheumatoid Factor: <14 IU/mL (Reference Range: <14)
    """
    
    with open(samples_dir / "lab_result_sample.txt", "w") as f:
        f.write(lab_result)
    
    # Sample medical note
    medical_note = """
    CLINICAL NOTE
    Date: 2023-07-12
    Patient: Jane Smith
    Provider: Dr. Robert Johnson, MD, Rheumatology
    
    CHIEF COMPLAINT:
    Joint pain and hypermobility
    
    HISTORY OF PRESENT ILLNESS:
    Patient is a 35-year-old female presenting with chronic joint pain, particularly in the knees, wrists, and fingers. She reports joint hypermobility since childhood and frequent subluxations. Patient also reports skin hyperextensibility and easy bruising. Family history significant for similar symptoms in mother.
    
    MEDICATIONS:
    - Ibuprofen 600 mg as needed for pain
    - Tramadol 50 mg daily as needed for severe pain
    - Vitamin D 2000 IU daily
    
    VITAL SIGNS:
    BP: 118/78
    HR: 72
    Temp: 98.6 F
    RR: 16
    O2: 99% RA
    
    ASSESSMENT:
    Patient presents with classic signs of Ehlers-Danlos Syndrome, hypermobility type. Beighton score of 8/9. Meets criteria for hEDS diagnosis. Will also evaluate for POTS and MCAS given common comorbidity with EDS. 
    
    PLAN:
    1. Refer to physical therapy for joint stabilization exercises
    2. Order echocardiogram to rule out valvular issues
    3. Refer to genetics for confirmation and family counseling
    4. Recommend compression stockings and increased salt/fluid intake for dysautonomia symptoms
    5. Return in 3 months for follow-up
    """
    
    with open(samples_dir / "medical_note_sample.txt", "w") as f:
        f.write(medical_note)
    
    # Sample patient narrative
    patient_narrative = """
    My Symptom Journal
    Date: 2023-08-01
    
    I've been experiencing increased sensory sensitivity over the past month. Bright lights and loud sounds are particularly difficult to process, often triggering headaches. I've also noticed increased difficulty with executive function tasks and have been struggling with task initiation and completion.
    
    My special interest in medical research has been both helpful for understanding my symptoms and sometimes overwhelming. I find myself hyperfocusing on research for hours, which can lead to burnout.
    
    Social interactions continue to be challenging, and I've been consciously masking less to preserve energy. However, this has led to increased anxiety in public settings. Stimming (rocking, hand flapping) helps regulate my nervous system but attracts unwanted attention.
    
    Medication update:
    - Started Propranolol 10 mg twice daily for anxiety/POTS symptoms
    - Vitamin B12 1000 mcg daily for energy
    
    I suspect my autistic traits and ADHD symptoms are being exacerbated by my physical health issues (EDS, POTS). The chronic pain (currently 6/10 in joints) seems to reduce my capacity for sensory processing and executive functioning.
    """
    
    with open(samples_dir / "patient_narrative_sample.txt", "w") as f:
        f.write(patient_narrative)


if __name__ == "__main__":
    test_with_sample_files() 