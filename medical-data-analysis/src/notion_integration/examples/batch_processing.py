#!/usr/bin/env python3
"""
Batch Processing Example - Medical Data to Notion Integration

This example demonstrates how to process multiple medical documents in batch
and sync the extracted data to your Notion databases.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directories to path for imports
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir.parent.parent))

from notion_integration.medical_data_processor import MedicalDataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("batch_processing")


def infer_document_type(file_path: str) -> str:
    """
    Infer document type from file name or path
    
    Args:
        file_path: Path to the document
        
    Returns:
        Inferred document type
    """
    lower_path = file_path.lower()
    
    if "lab" in lower_path or "test" in lower_path or "result" in lower_path:
        return "lab_result"
    elif "visit" in lower_path or "appointment" in lower_path or "note" in lower_path:
        return "clinical_note"
    elif "medication" in lower_path or "prescription" in lower_path:
        return "medication_list"
    elif "radiology" in lower_path or "imaging" in lower_path or "xray" in lower_path:
        return "imaging_report"
    elif "hospital" in lower_path or "discharge" in lower_path:
        return "hospital_note"
    else:
        return "general_medical_document"


def infer_document_date(file_path: str) -> str:
    """
    Try to infer document date from file name using common patterns
    
    Args:
        file_path: Path to the document
        
    Returns:
        Inferred date in ISO format, or current date if not found
    """
    file_name = Path(file_path).name
    
    # Look for YYYY-MM-DD pattern
    import re
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
    if date_match:
        return date_match.group(1)
    
    # Look for MM-DD-YYYY pattern
    date_match = re.search(r'(\d{2}-\d{2}-\d{4})', file_name)
    if date_match:
        parts = date_match.group(1).split('-')
        return f"{parts[2]}-{parts[0]}-{parts[1]}"
    
    # Default to current date if no pattern found
    return datetime.now().strftime("%Y-%m-%d")


def process_directory(
    processor: MedicalDataProcessor,
    directory_path: str,
    extensions: List[str] = [".txt", ".pdf", ".csv", ".html", ".md"],
    recursive: bool = False
) -> Dict[str, Any]:
    """
    Process all medical documents in a directory
    
    Args:
        processor: MedicalDataProcessor instance
        directory_path: Path to directory containing medical documents
        extensions: File extensions to process
        recursive: Whether to process subdirectories recursively
        
    Returns:
        Processing statistics
    """
    if not os.path.isdir(directory_path):
        logger.error(f"{directory_path} is not a valid directory")
        return {"error": "Invalid directory", "files_processed": 0}
    
    stats = {
        "total_files": 0,
        "processed_files": 0,
        "failed_files": 0,
        "appointments_created": 0,
        "medications_created": 0,
        "conditions_created": 0,
        "symptoms_created": 0,
        "providers_created": 0,
        "errors": []
    }
    
    # Get list of files to process
    files_to_process = []
    
    if recursive:
        for root, _, files in os.walk(directory_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    files_to_process.append(os.path.join(root, file))
    else:
        files_to_process = [
            os.path.join(directory_path, f) for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f)) and 
            any(f.lower().endswith(ext) for ext in extensions)
        ]
    
    stats["total_files"] = len(files_to_process)
    logger.info(f"Found {len(files_to_process)} files to process")
    
    # Process each file
    for file_path in files_to_process:
        try:
            file_name = os.path.basename(file_path)
            logger.info(f"Processing {file_name}...")
            
            document_type = infer_document_type(file_path)
            document_date = infer_document_date(file_path)
            
            # Process the file based on its extension
            if file_path.lower().endswith(".pdf"):
                result = processor.process_pdf(
                    pdf_path=file_path,
                    document_type=document_type,
                    document_date=document_date
                )
            elif file_path.lower().endswith(".csv"):
                result = processor.process_csv(
                    csv_path=file_path,
                    document_type=document_type,
                    document_date=document_date
                )
            else:
                # Default to text processing for other formats
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                result = processor.process_text(
                    text=text_content,
                    document_type=document_type,
                    document_date=document_date
                )
            
            # Update statistics
            stats["processed_files"] += 1
            stats["appointments_created"] += len(result.get("appointments", []))
            stats["medications_created"] += len(result.get("medications", []))
            stats["conditions_created"] += len(result.get("conditions", []))
            stats["symptoms_created"] += len(result.get("symptoms", []))
            stats["providers_created"] += len(result.get("providers", []))
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            stats["failed_files"] += 1
            stats["errors"].append({"file": file_path, "error": str(e)})
    
    return stats


def main():
    """Main function for batch processing example"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process medical documents in batch")
    parser.add_argument("--dir", "-d", required=True, help="Directory containing medical documents")
    parser.add_argument("--config", "-c", default="notion_config.json", help="Path to configuration file")
    parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
    args = parser.parse_args()
    
    # Load configuration
    config_path = args.config
    if not os.path.exists(config_path):
        config_path = script_dir / "notion_config.json"
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found at {config_path}")
        logger.error("Please create a configuration file with your API keys and database IDs")
        return
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Create processor instance
    processor = MedicalDataProcessor(config=config)
    
    # Process the directory
    logger.info(f"Processing files in {args.dir}...")
    stats = process_directory(
        processor=processor,
        directory_path=args.dir,
        recursive=args.recursive
    )
    
    # Log results
    logger.info(f"Processing complete.")
    logger.info(f"Files processed: {stats['processed_files']}/{stats['total_files']}")
    logger.info(f"Files failed: {stats['failed_files']}")
    logger.info(f"Appointments created: {stats['appointments_created']}")
    logger.info(f"Medications created: {stats['medications_created']}")
    logger.info(f"Conditions created: {stats['conditions_created']}")
    logger.info(f"Symptoms created: {stats['symptoms_created']}")
    logger.info(f"Providers created: {stats['providers_created']}")
    
    if stats['errors']:
        logger.info(f"Errors encountered during processing:")
        for error in stats['errors']:
            logger.info(f"  - {os.path.basename(error['file'])}: {error['error']}")


if __name__ == "__main__":
    main() 