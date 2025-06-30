#!/usr/bin/env python3
"""
Example script for processing medical documents and syncing to Notion.

This script demonstrates how to use the MedicalDataProcessor to extract
medical entities from documents and create entries in Notion databases.
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notion_integration.medical_data_processor import MedicalDataProcessor


def create_config_file():
    """Create a sample configuration file if it doesn't exist"""
    config_path = "notion_config.json"
    
    if os.path.exists(config_path):
        print(f"Config file already exists at {config_path}")
        return config_path
    
    config = {
        "notion_token": "YOUR_NOTION_TOKEN",
        "openai_key": "YOUR_OPENAI_KEY",
        "notion_databases": {
            "calendar": "17b86edc-ae2c-81c1-83e0-e0a19a035932",
            "doctors": "17b86edc-ae2c-8155-8caa-fbb80647f6a9",
            "diagnosis": "17b86edc-ae2c-8167-ba15-f9f03b49795e",
            "symptoms": "17b86edc-ae2c-81c6-9077-e55a68cf2438",
            "medications": "17b86edc-ae2c-81a7-b28a-e9fbcc7e7b62"
        }
    }
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Created sample config file at {config_path}")
    print("Please update it with your actual API keys before running the example.")
    return config_path


def process_sample_document(processor, file_path):
    """Process a sample document and display extracted entities"""
    print(f"\nProcessing document: {file_path}")
    
    # Extract entities from the document
    print("Extracting medical entities...")
    extracted_data = processor.process_document(file_path)
    
    # Print summary of extracted entities
    print("\nExtracted Entity Summary:")
    for entity_type, entities in extracted_data.items():
        print(f"  {entity_type.capitalize()}: {len(entities)} entities found")
    
    # Print detailed view of extracted entities (first of each type)
    print("\nDetailed View (first entity of each type):")
    for entity_type, entities in extracted_data.items():
        if entities:
            print(f"\n{entity_type.capitalize()}:")
            print(json.dumps(entities[0], indent=2))
    
    # Sync to Notion
    print("\nSyncing to Notion...")
    sync_results = processor.create_notion_entries(extracted_data)
    
    # Print results
    print("\nSync Results:")
    for status, counts in sync_results.items():
        print(f"  {status.capitalize()}:")
        for entity_type, count in counts.items():
            print(f"    {entity_type}: {count}")
    
    return extracted_data, sync_results


def main():
    """Main entry point for the example script"""
    print("Medical Data Processor Example")
    print("==============================")
    
    # Create sample config file if needed
    config_path = create_config_file()
    
    # Check if API keys have been set
    with open(config_path, "r") as f:
        config = json.load(f)
    
    if config["notion_token"] == "YOUR_NOTION_TOKEN" or config["openai_key"] == "YOUR_OPENAI_KEY":
        print("\nError: Please update the config file with your actual API keys.")
        sys.exit(1)
    
    # Initialize processor
    print("\nInitializing MedicalDataProcessor...")
    processor = MedicalDataProcessor(
        notion_token=config["notion_token"],
        openai_key=config["openai_key"]
    )
    
    # Prompt for document path
    file_path = input("\nEnter path to a medical document file: ")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Process the document
    process_sample_document(processor, file_path)
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main() 