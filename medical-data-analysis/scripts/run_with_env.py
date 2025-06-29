#!/usr/bin/env python3
"""
Medical Data to Notion Integration Runner

This script runs the medical data to Notion integration using environment variables.
It loads API keys from the .env file and runs the data syncer.
"""

import os
import sys
import argparse
import logging
import json
import subprocess
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'sync.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run Medical Data to Notion Integration')
    parser.add_argument('--input', type=str, default='data/input',
                        help='Input directory containing medical documents')
    parser.add_argument('--recursive', action='store_true',
                        help='Process input directory recursively')
    parser.add_argument('--include-content', action='store_true',
                        help='Include original document content in Notion')
    parser.add_argument('--extensions', type=str, default='.txt,.pdf,.html,.docx,.md,.rtf,.csv',
                        help='File extensions to process (comma-separated)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()

def main():
    """Main function to run the integration"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "NOTION_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please create a .env file with these variables or set them in your environment")
        sys.exit(1)
    
    # Parse command line arguments
    args = parse_args()
    
    # Create a temporary config file with environment variables
    config = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2048"))
        },
        "notion": {
            "token": os.getenv("NOTION_TOKEN"),
            "databases": {
                "medical_calendar": os.getenv("NOTION_MEDICAL_CALENDAR_DB", "17b86edc-ae2c-81c1-83e0-e0a19a035932"),
                "medical_team": os.getenv("NOTION_MEDICAL_TEAM_DB", "17b86edc-ae2c-8155-8caa-fbb80647f6a9"),
                "medical_conditions": os.getenv("NOTION_MEDICAL_CONDITIONS_DB", "17b86edc-ae2c-8167-ba15-f9f03b49795e"),
                "medications": os.getenv("NOTION_MEDICATIONS_DB", "17b86edc-ae2c-81a7-b28a-e9fbcc7e7b62"),
                "symptoms": os.getenv("NOTION_SYMPTOMS_DB", "17b86edc-ae2c-81c6-9077-e55a68cf2438")
            }
        },
        "extraction": {
            "chunk_size": int(os.getenv("EXTRACTION_CHUNK_SIZE", "4000")),
            "chunk_overlap": int(os.getenv("EXTRACTION_CHUNK_OVERLAP", "200")),
            "min_confidence": float(os.getenv("EXTRACTION_MIN_CONFIDENCE", "0.7")),
            "entity_types": ["appointments", "medications", "conditions", "symptoms", "providers"]
        },
        "processing": {
            "update_existing": os.getenv("PROCESSING_UPDATE_EXISTING", "true").lower() == "true",
            "create_missing_relations": os.getenv("PROCESSING_CREATE_MISSING_RELATIONS", "true").lower() == "true",
            "auto_merge_similar_entities": os.getenv("PROCESSING_AUTO_MERGE", "true").lower() == "true",
            "preserve_original_text": os.getenv("PROCESSING_PRESERVE_ORIGINAL", "true").lower() == "true",
            "detect_duplicates": os.getenv("PROCESSING_DETECT_DUPLICATES", "true").lower() == "true"
        },
        "logging": {
            "level": os.getenv("LOGGING_LEVEL", "INFO"),
            "log_to_file": os.getenv("LOGGING_TO_FILE", "true").lower() == "true",
            "log_dir": os.getenv("LOGGING_DIR", "logs")
        }
    }
    
    # Write config to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_config:
        json.dump(config, temp_config, indent=2)
        temp_config_path = temp_config.name
        
    logger.info(f"Created temporary config file at {temp_config_path}")
    
    try:
        # Build command to run the syncer script
        cmd = [
            "python", "-m", "src.notion_integration.notion_data_syncer",
            "--config", temp_config_path,
            "--input", args.input
        ]
        
        if args.recursive:
            cmd.append("--recursive")
            
        if args.include_content:
            cmd.append("--include-content")
            
        if args.extensions:
            cmd.extend(["--extensions", args.extensions])
            
        if args.verbose:
            cmd.append("--verbose")
        
        # Run the command
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd, check=True)
        
        if process.returncode == 0:
            logger.info("Notion integration completed successfully!")
        else:
            logger.error(f"Notion integration failed with code {process.returncode}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Notion integration: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary config file
        try:
            os.unlink(temp_config_path)
        except:
            pass

if __name__ == "__main__":
    main() 