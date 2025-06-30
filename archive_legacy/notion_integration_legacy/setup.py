#!/usr/bin/env python3
"""
Setup script for the Medical Data to Notion Integration

This script helps with initial setup, including configuration creation,
directory structure, and dependency installation.
"""

import os
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path
import subprocess
from setuptools import setup, find_packages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup")


def create_config_file(output_path: str, overwrite: bool = False) -> bool:
    """
    Create a configuration file template
    
    Args:
        output_path: Path where to create the configuration file
        overwrite: Whether to overwrite an existing file
        
    Returns:
        True if created successfully, False otherwise
    """
    if os.path.exists(output_path) and not overwrite:
        logger.error(f"Configuration file already exists at {output_path}")
        logger.error("Use --overwrite to replace it.")
        return False
    
    # Template configuration
    config = {
        "openai": {
            "api_key": "",
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 2048
        },
        "notion": {
            "token": "",
            "databases": {
                "medical_calendar": "",
                "medical_team": "",
                "medical_conditions": "",
                "medications": "",
                "symptoms": ""
            }
        },
        "extraction": {
            "chunk_size": 4000,
            "chunk_overlap": 200,
            "min_confidence": 0.7,
            "entity_types": [
                "appointments",
                "medications",
                "conditions",
                "symptoms",
                "providers"
            ]
        },
        "processing": {
            "update_existing": True,
            "create_missing_relations": True,
            "auto_merge_similar_entities": True,
            "preserve_original_text": True,
            "detect_duplicates": True
        },
        "logging": {
            "level": "INFO",
            "log_to_file": True,
            "log_dir": "logs"
        }
    }
    
    try:
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Created configuration template at {output_path}")
        logger.info("Please edit this file to add your API keys and database IDs")
        return True
    
    except Exception as e:
        logger.error(f"Error creating configuration file: {str(e)}")
        return False


def create_directory_structure(base_dir: str) -> bool:
    """
    Create the necessary directory structure
    
    Args:
        base_dir: Base directory to create subdirectories in
        
    Returns:
        True if created successfully, False otherwise
    """
    directories = [
        "data/input",
        "data/output",
        "data/processed",
        "logs",
        "examples"
    ]
    
    try:
        for directory in directories:
            dir_path = os.path.join(base_dir, directory)
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating directory structure: {str(e)}")
        return False


def install_dependencies() -> bool:
    """
    Install required dependencies
    
    Returns:
        True if installed successfully, False otherwise
    """
    try:
        # Find requirements.txt
        script_dir = Path(__file__).resolve().parent
        requirements_path = script_dir / "requirements.txt"
        
        if not requirements_path.exists():
            logger.error(f"Requirements file not found at {requirements_path}")
            return False
        
        logger.info("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
        logger.info("Dependencies installed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        return False


def main():
    """Main function for setup script"""
    parser = argparse.ArgumentParser(description="Setup Medical Data to Notion Integration")
    parser.add_argument("--config", "-c", default="notion_config.json", help="Path for configuration file")
    parser.add_argument("--data-dir", "-d", default="data", help="Path for data directory")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Overwrite existing files")
    parser.add_argument("--skip-deps", "-s", action="store_true", help="Skip dependency installation")
    args = parser.parse_args()
    
    # Create configuration file
    logger.info("Setting up Medical Data to Notion Integration...")
    create_config_file(args.config, args.overwrite)
    
    # Create directory structure
    create_directory_structure(os.getcwd())
    
    # Install dependencies
    if not args.skip_deps:
        install_dependencies()
    
    logger.info("Setup complete!")
    logger.info(f"Edit {args.config} to add your API keys and database IDs")
    logger.info("Run the examples to test your setup:")
    logger.info("  python -m examples.simple_example --config notion_config.json")
    logger.info("  python -m examples.batch_processing --dir data/input --config notion_config.json")


if __name__ == "__main__":
    main()

setup(
    name="notion_integration",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "langchain",
        "notion-client",
        "openai",
        "python-dotenv",
        "pypdf",
        "html2text",
        "python-docx",
        "bs4",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "notion-sync=notion_integration.notion_data_syncer:main",
        ],
    },
) 