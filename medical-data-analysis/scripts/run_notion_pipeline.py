#!/usr/bin/env python3
"""
Run the full medical data pipeline to process and import data to Notion.

This script coordinates the entire process of:
1. Extracting medical data from processed files
2. Formatting the data for Notion import
3. Importing the data into Notion databases
"""
import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notion_pipeline")

def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure an argument parser."""
    parser = argparse.ArgumentParser(
        description="Run medical data pipeline for Notion import"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="processed_data",
        help="Directory with processed medical data (default: processed_data)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Output directory for formatted data (default: data)"
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        default="config",
        help="Configuration directory (default: config)"
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=0,
        help="Maximum number of events to process (0 = no limit)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process data but don't import to Notion"
    )
    return parser

def run_script(script_path: str, args: Optional[List[str]] = None) -> bool:
    """
    Run a Python script with the given arguments.
    
    Args:
        script_path: Path to the script
        args: List of command line arguments
        
    Returns:
        True if the script executed successfully, False otherwise
    """
    command = [sys.executable, script_path]
    
    if args:
        command.extend(args)
    
    logger.info(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Command output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with code {e.returncode}")
        logger.error(f"Error output: {e.stderr.strip()}")
        return False

def check_environment() -> bool:
    """
    Check if the environment is properly set up.
    
    Returns:
        True if the environment is valid, False otherwise
    """
    # Check for NOTION_API_KEY or NOTION_TOKEN
    api_token = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
    if not api_token:
        logger.error("Neither NOTION_API_KEY nor NOTION_TOKEN environment variable is set")
        logger.info("Please set one of these environment variables:")
        logger.info("export NOTION_API_KEY='your_api_key'")
        logger.info("  or")
        logger.info("export NOTION_TOKEN='your_api_key'")
        return False
    
    # Check for required directories
    required_dirs = ["config", "scripts", "data"]
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            logger.error(f"Required directory '{dir_name}' not found")
            return False
    
    # Check for required config files
    required_configs = ["config/notion_config.json", "config/notion_field_mapping.json"]
    for config_file in required_configs:
        if not os.path.isfile(config_file):
            logger.error(f"Required configuration file '{config_file}' not found")
            return False
    
    return True

def main():
    """Main entry point for the script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Please fix the issues and try again.")
        return 1
    
    # Create necessary directories
    os.makedirs(args.output_dir, exist_ok=True)
    
    output_events_file = os.path.join(args.output_dir, 'medical_events.json')
    
    # Step 1: Extract medical data (skip if output file already exists)
    if os.path.exists(output_events_file) and os.path.getsize(output_events_file) > 0:
        logger.info(f"Using existing medical events from {output_events_file}")
    else:
        extract_script = "scripts/extract_medical_data.py"
        extract_args = [
            f"--input-dir={args.input_dir}",
            f"--output-file={output_events_file}"
        ]
        
        if args.max_events > 0:
            extract_args.append(f"--max-events={args.max_events}")
        
        if not run_script(extract_script, extract_args):
            logger.error("Data extraction failed. Pipeline stopping.")
            return 1
    
    # Step 2: Format data for Notion
    format_script = "scripts/format_for_notion.py"
    format_args = [
        f"--input-file={output_events_file}",
        f"--output-file={os.path.join(args.output_dir, 'notion_formatted_events.json')}",
        f"--field-mapping={os.path.join(args.config_dir, 'notion_field_mapping.json')}"
    ]
    
    if not run_script(format_script, format_args):
        logger.error("Data formatting failed. Pipeline stopping.")
        return 1
    
    # Step 3: Import data to Notion (unless dry run)
    if args.dry_run:
        logger.info("Dry run: Skipping Notion import")
    else:
        import_script = "scripts/import_to_notion.py"
        import_args = [
            f"--input-file={os.path.join(args.output_dir, 'notion_formatted_events.json')}",
            f"--config-file={os.path.join(args.config_dir, 'notion_config.json')}"
        ]
        
        if not run_script(import_script, import_args):
            logger.error("Notion import failed.")
            return 1
    
    logger.info("Pipeline completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 