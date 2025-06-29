#!/usr/bin/env python3
"""
End-to-End Example for Medical Data to Notion Integration

This script demonstrates a complete workflow for processing medical documents
and syncing extracted data to Notion databases.

Usage:
    python end_to_end_example.py
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path

# Add the parent directory to sys.path to allow importing from notion_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from notion_integration.medical_data_processor import MedicalDataProcessor
from notion_integration.config import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run an end-to-end example of medical data processing and Notion integration"""
    parser = argparse.ArgumentParser(description="Run a medical data to Notion integration example")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--sample", type=str, help="Path to sample medical document")
    parser.add_argument("--create-config", action="store_true", help="Create a sample config file")
    
    args = parser.parse_args()
    
    # Create a sample configuration file if requested
    if args.create_config:
        config_path = args.config or "notion_config_sample.json"
        create_sample_config(config_path)
        logger.info(f"Created sample configuration file at: {config_path}")
        logger.info("Please edit this file to add your API keys and database IDs before running the example")
        return
    
    # Use provided configuration or look for default
    config_path = args.config
    if not config_path:
        # Check for config file in current directory
        default_config = "notion_config.json"
        if os.path.exists(default_config):
            config_path = default_config
        else:
            logger.error("No configuration file provided and no default config found")
            logger.info("Run with --create-config to create a sample configuration file")
            return
    
    # Verify configuration file exists
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        return
    
    # Sample document handling
    sample_doc = args.sample
    if not sample_doc:
        logger.info("No sample document provided, using a text example")
        # Create a sample text document
        sample_doc = create_sample_document()
    elif not os.path.exists(sample_doc):
        logger.error(f"Sample document not found: {sample_doc}")
        return
    
    # Initialize the medical data processor
    logger.info("Initializing the medical data processor...")
    processor = MedicalDataProcessor(config_path=config_path)
    
    # Process the sample document
    logger.info(f"Processing document: {sample_doc}")
    extracted_data = processor.process_document(sample_doc)
    
    # Display the extracted entities
    logger.info("=== Extracted Entities ===")
    for entity_type, entities in extracted_data.items():
        if entities:
            logger.info(f"{entity_type.capitalize()}: {len(entities)}")
            for entity in entities[:2]:  # Show only first 2 for brevity
                logger.info(f"  - {entity.get('name', entity.get('title', 'Unnamed'))}")
            if len(entities) > 2:
                logger.info(f"  - ... and {len(entities) - 2} more")
    
    # Ask for confirmation before syncing to Notion
    confirm = input("\nDo you want to sync these entities to your Notion databases? (yes/no): ")
    if confirm.lower() not in ["yes", "y"]:
        logger.info("Sync cancelled by user")
        return
    
    # Sync to Notion
    logger.info("Syncing data to Notion...")
    notion_results = processor.create_notion_entries(extracted_data)
    
    # Display the results
    logger.info("=== Notion Sync Results ===")
    if "created" in notion_results:
        logger.info("Created entities:")
        for entity_type, count in notion_results["created"].items():
            if count > 0:
                logger.info(f"  - {entity_type}: {count}")
    
    if "updated" in notion_results:
        logger.info("Updated entities:")
        for entity_type, count in notion_results["updated"].items():
            if count > 0:
                logger.info(f"  - {entity_type}: {count}")
    
    if "skipped" in notion_results:
        logger.info("Skipped entities:")
        for entity_type, count in notion_results["skipped"].items():
            if count > 0:
                logger.info(f"  - {entity_type}: {count}")
    
    logger.info("\nEnd-to-end example completed successfully!")


def create_sample_config(file_path: str) -> None:
    """Create a sample configuration file"""
    sample_config = {
        "notion": {
            "token": "your_notion_api_token_here",
            "databases": {
                "medical_calendar": "medical_calendar_database_id_here",
                "medical_team": "medical_team_database_id_here",
                "medical_conditions": "medical_conditions_database_id_here",
                "symptoms": "symptoms_database_id_here",
                "medications": "medications_database_id_here"
            }
        },
        "openai": {
            "api_key": "your_openai_api_key_here",
            "model": "gpt-4o",
            "temperature": 0.1
        },
        "extraction": {
            "chunk_size": 4000,
            "chunk_overlap": 200,
            "default_document_type": "medical_document"
        },
        "processing": {
            "default_extensions": [".pdf", ".txt", ".html", ".docx", ".rtf", ".csv", ".md"],
            "max_workers": 2
        }
    }
    
    with open(file_path, 'w') as f:
        json.dump(sample_config, f, indent=2)


def create_sample_document() -> str:
    """Create a sample medical document for testing"""
    sample_content = """
VISIT SUMMARY
Date: 2023-04-15
Provider: Dr. Sarah Johnson, Rheumatology
Patient: Jane Doe

CHIEF COMPLAINT:
Joint pain, fatigue, and skin hypermobility

HISTORY OF PRESENT ILLNESS:
Patient is a 32-year-old female with a history of hypermobile joints who presents with worsening joint pain and fatigue over the past 3 months. She reports pain primarily in fingers, wrists, knees, and ankles. Patient also notes that her skin is unusually stretchy and bruises easily. She has been experiencing daily headaches for the past 6 weeks. Patient reports that she was previously diagnosed with ADHD in 2018 and has recently been experiencing increased sensory sensitivity.

MEDICATIONS:
1. Adderall XR 20mg once daily for ADHD
2. Cymbalta 60mg once daily for pain management
3. Vitamin D3 5000 IU daily
4. Magnesium glycinate 400mg at bedtime for muscle tension

ASSESSMENT:
1. Hypermobility Spectrum Disorder - Patient meets criteria for generalized hypermobility with Beighton score of 7/9. Given family history and additional systemic manifestations, suspect hEDS.
2. Chronic Pain Syndrome - Likely related to hypermobility
3. ADHD - Currently stable on medication
4. Possible POTS - Noted tachycardia upon standing during today's exam

PLAN:
1. Referral to genetics for evaluation of Ehlers-Danlos Syndrome
2. Start physical therapy 2x weekly for joint stabilization
3. Labs ordered: CMP, CBC, ESR, CRP, vitamin levels, and cardiac markers
4. Trial of compression stockings for possible POTS
5. Continue current medications
6. Follow-up appointment in 3 months

FOLLOW-UP:
Schedule with Dr. Johnson in 3 months
Genetics consultation with Dr. Michelle Lee - referral sent
Cardiology appointment for POTS evaluation - referral sent to Dr. Robert Garcia

Dr. Sarah Johnson, MD
Rheumatology Specialists
123 Medical Center Dr.
Phone: (555) 123-4567
"""
    
    # Save the sample content to a temporary file
    temp_file = "sample_medical_document.txt"
    with open(temp_file, 'w') as f:
        f.write(sample_content)
    
    return temp_file


if __name__ == "__main__":
    main() 