#!/usr/bin/env python3
"""
Sync Medical Data

This script loads configurations, environment variables, and runs the medical data sync process.
"""

import os
import sys
import json
import uuid
import logging
import tempfile
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the medical data sync process"""
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    notion_token = os.getenv("NOTION_TOKEN")
    
    if not openai_api_key:
        logger.error("Missing OpenAI API key. Please set OPENAI_API_KEY in your .env file.")
        return 1
    
    if not notion_token:
        logger.error("Missing Notion API token. Please set NOTION_TOKEN in your .env file.")
        return 1
    
    # Load the config with database IDs
    config_path = Path("config/notion_config.json")
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return 1
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        return 1
    
    # Create a temporary config with API keys
    temp_config = config.copy()
    temp_config["openai"]["api_key"] = openai_api_key
    temp_config["notion"]["token"] = notion_token
    
    # Write the temporary config
    fd, temp_config_path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(temp_config, f, indent=2)
        
        # Build the command to run the sync
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent)
        
        cmd = [
            sys.executable, 
            "src/notion_integration/notion_data_syncer.py",
            "--config", temp_config_path,
            "--input", "data/input",
            "--recursive",
            "--include-content"
        ]
        
        try:
            logger.info("Starting medical data sync...")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Run the sync process
            proc = subprocess.run(cmd, check=True, env=env)
            
            logger.info("Sync completed successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Sync process failed with code {e.returncode}")
            return e.returncode
    finally:
        # Clean up the temporary config file
        try:
            os.unlink(temp_config_path)
        except OSError:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 