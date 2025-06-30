#!/usr/bin/env python3
"""
Simple Example - Medical Data to Notion Integration

This example demonstrates basic usage of the Medical Data to Notion integration.
It processes a simple medical note and creates entries in Notion databases.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent directories to path for imports
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir.parent.parent))

from notion_integration.medical_data_processor import MedicalDataProcessor
from notion_integration.config import load_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_example")


def create_sample_medical_note() -> str:
    """Create a sample medical note for demonstration purposes"""
    sample_note_path = "sample_medical_note.txt"
    
    if os.path.exists(sample_note_path):
        logger.info(f"Using existing sample note at {sample_note_path}")
        with open(sample_note_path, "r") as f:
            return f.read()
    
    # Create a new sample note
    sample_note = """
PATIENT VISIT NOTE
Date: 2023-11-15
Provider: Dr. Sarah Johnson
Specialty: Rheumatology

REASON FOR VISIT
Patient presents with joint pain, particularly in the hands, wrists, and knees. Reports fatigue and morning stiffness lasting approximately 1 hour.

MEDICATIONS
- Ibuprofen 600mg PRN for pain
- Hydroxychloroquine 200mg daily
- Vitamin D 2000 IU daily
- Calcium 500mg daily

ASSESSMENT
Patient shows signs consistent with early rheumatoid arthritis. Symptoms have been present for approximately 3 months and are affecting daily activities.

PLAN
1. Continue hydroxychloroquine 200mg daily
2. Refer to physical therapy for joint exercises
3. Order rheumatoid factor and anti-CCP antibody tests
4. Follow up in 4 weeks to assess medication efficacy
5. Recommended to maintain moderate physical activity as tolerated

UPCOMING APPOINTMENTS
Physical Therapy: 2023-11-22, 10:00 AM with Dr. James Miller
Lab Work: 2023-11-18, 8:30 AM at Main Campus Laboratory
Follow-up: 2023-12-13, 9:15 AM with Dr. Sarah Johnson
"""
    
    # Save the sample note to a file
    with open(sample_note_path, "w") as f:
        f.write(sample_note)
    
    logger.info(f"Created sample medical note at {sample_note_path}")
    return sample_note


def main():
    """Main function demonstrating the integration workflow"""
    # Load configuration
    config_path = script_dir / "notion_config.json"
    if not config_path.exists():
        # Create a template config file if it doesn't exist
        template_config = {
            "notion": {
                "token": "your_notion_api_token",
                "databases": {
                    "medical_calendar": "your_medical_calendar_database_id",
                    "medical_team": "your_medical_team_database_id",
                    "medical_conditions": "your_medical_conditions_database_id",
                    "medications": "your_medications_database_id",
                    "symptoms": "your_symptoms_database_id"
                }
            },
            "openai": {
                "api_key": "your_openai_api_key",
                "model": "gpt-4o",
                "temperature": 0.1
            }
        }
        
        with open(config_path, "w") as f:
            json.dump(template_config, f, indent=2)
        
        logger.error(f"Configuration file not found. Created template at {config_path}")
        logger.error("Please edit the configuration file with your API keys and database IDs.")
        return
    
    # Load the configuration
    config = load_config(config_path)
    
    # Create a processor instance
    processor = MedicalDataProcessor(config)
    
    # Create a sample medical note
    sample_note = create_sample_medical_note()
    
    logger.info("Processing sample medical note...")
    
    # Process the note (in a real scenario, you'd load from a file)
    result = processor.process_text(
        text=sample_note,
        document_type="clinical_note",
        document_date="2023-11-15"
    )
    
    # Log the results
    logger.info(f"Processing complete. Results:")
    logger.info(f"Appointments created: {len(result.get('appointments', []))}")
    logger.info(f"Medications created/updated: {len(result.get('medications', []))}")
    logger.info(f"Conditions created/updated: {len(result.get('conditions', []))}")
    logger.info(f"Symptoms created/updated: {len(result.get('symptoms', []))}")
    logger.info(f"Providers created/updated: {len(result.get('providers', []))}")
    
    logger.info("Check your Notion databases to see the created entries.")


if __name__ == "__main__":
    main() 