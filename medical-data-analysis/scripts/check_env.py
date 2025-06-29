#!/usr/bin/env python3
"""
Check Environment

This script checks if the required environment variables are set.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_env_variables():
    """Check required environment variables"""
    # Load environment variables
    load_dotenv()
    
    # Environment variables to check
    env_vars = {
        "OPENAI_API_KEY": "OpenAI API key for entity extraction",
        "NOTION_TOKEN": "Notion API token for data syncing"
    }
    
    missing = []
    for var, description in env_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(var)
            logger.error(f"Missing {var}: {description}")
        else:
            # Only show first few characters of API keys for security
            display_value = value[:4] + "..." + value[-4:] if len(value) > 10 else "***"
            logger.info(f"✓ {var} is set: {display_value}")
    
    # Check config files
    config_files = [
        "config/notion_config.json",
        "config/notion_field_mapping.json"
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            logger.info(f"✓ {file_path} exists")
        else:
            logger.error(f"Missing {file_path}")
            missing.append(file_path)
    
    return len(missing) == 0

def main():
    """Main entry point"""
    logger.info("Checking environment variables and configuration...")
    
    if check_env_variables():
        logger.info("All required environment variables and configuration files are set!")
        return 0
    else:
        logger.error("Some required environment variables or configuration files are missing.")
        logger.info("Please create a .env file in the project root with the required variables.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 