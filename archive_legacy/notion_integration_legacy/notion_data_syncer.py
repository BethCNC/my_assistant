#!/usr/bin/env python
"""
Medical Data to Notion Syncer

This script processes medical documents and syncs extracted entities to Notion databases.
"""

import argparse
import logging
import os
import json
import sys
from pathlib import Path

# Import from the current module directory
try:
    from medical_data_processor import MedicalDataProcessor
except ImportError:
    # Try relative import if being run as a module
    try:
        from .medical_data_processor import MedicalDataProcessor
    except ImportError:
        # Try absolute import if being run from outside as a script
        from src.notion_integration.medical_data_processor import MedicalDataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("notion_sync.log")
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_path):
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Sync medical data to Notion")
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--input", required=True, help="Path to input directory or file")
    parser.add_argument("--recursive", action="store_true", help="Process directories recursively")
    parser.add_argument("--include-content", action="store_true", help="Include document content in Notion")
    parser.add_argument("--extensions", help="Comma-separated list of file extensions to process")
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Create processor
        processor = MedicalDataProcessor(config)
        
        # Get file extensions
        extensions = None
        if args.extensions:
            extensions = [ext.strip() for ext in args.extensions.split(",")]
            if not all(ext.startswith(".") for ext in extensions):
                extensions = [f".{ext}" if not ext.startswith(".") else ext for ext in extensions]
        
        # Process input path
        input_path = Path(args.input)
        
        if input_path.is_file():
            # Process single file
            logger.info(f"Processing single file: {input_path}")
            result = processor.process_document(input_path, include_content=args.include_content)
            logger.info(f"File processed successfully: {input_path}")
            
        elif input_path.is_dir():
            # Process directory
            logger.info(f"Processing directory: {input_path}")
            result = processor.process_directory(
                input_path,
                recursive=args.recursive,
                file_extensions=extensions
            )
            logger.info(f"Directory processed successfully: {input_path}")
            
        else:
            logger.error(f"Input path not found: {input_path}")
            sys.exit(1)
        
        # Print summary
        entity_count = 0
        for entity_type, entities in result.items():
            if isinstance(entities, list):
                count = len(entities)
                entity_count += count
                logger.info(f"Synced {count} {entity_type}")
        
        logger.info(f"Total entities synced: {entity_count}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 