#!/usr/bin/env python3
"""
Master script to extract all medical events from all sources.

This script runs all extraction methods and combines the results:
1. Standard extraction (create_events_from_extractions.py)
2. AI-enhanced extraction (extract_with_ai.py)
3. Timeline extraction (extract_from_timeline.py)
4. Life story extraction (extract_from_life_story.py)
"""
import os
import sys
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("extract_all")

def run_extraction_script(script_name: str, output_file: Path) -> bool:
    """
    Run an extraction script with the given output file.
    
    Args:
        script_name: Name of the script to run
        output_file: Path to output file
        
    Returns:
        True if script ran successfully, False otherwise
    """
    script_path = Path("scripts") / script_name
    
    if not script_path.exists():
        logger.error(f"Script not found: {script_path}")
        return False
    
    try:
        logger.info(f"Running {script_name} with output to {output_file}")
        result = subprocess.run(
            ["python", str(script_path), "--output", str(output_file)],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"{script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_name}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Exception running {script_name}: {e}")
        return False

def load_events_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Load events from a file.
    
    Args:
        file_path: Path to events file
        
    Returns:
        List of event dictionaries
    """
    if not file_path.exists():
        logger.warning(f"Events file does not exist: {file_path}")
        return []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            if isinstance(data, dict) and "events" in data:
                return data["events"]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected data format in {file_path}")
                return []
    except Exception as e:
        logger.error(f"Error loading events from {file_path}: {e}")
        return []

def save_events(events: List[Dict[str, Any]], output_file: Path) -> bool:
    """
    Save events to a file.
    
    Args:
        events: List of event dictionaries
        output_file: Path to output file
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_file.parent.mkdir(exist_ok=True)
        
        # Sort events by date
        events.sort(key=lambda x: x.get("date", "9999-99-99"))
        
        # Create metadata
        output_data = {
            "metadata": {
                "updated": datetime.now().isoformat(),
                "source": "combined_extraction",
                "event_count": len(events)
            },
            "events": events
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        logger.info(f"Saved {len(events)} events to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving events to {output_file}: {e}")
        return False

def combine_events(event_files):
    """
    Combine events from multiple files into a single list.
    
    Args:
        event_files: List of event file paths
        
    Returns:
        Combined list of events
    """
    all_events = []
    seen_keys = set()
    
    for file_path in event_files:
        try:
            # Skip if file doesn't exist
            if not os.path.exists(file_path):
                logger.warning(f"File doesn't exist: {file_path}")
                continue
                
            # Load events from file
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Extract events based on file format
            events = []
            if isinstance(data, dict) and "events" in data:
                events = data["events"]
            elif isinstance(data, list):
                events = data
                
            logger.info(f"Loaded {len(events)} events from {file_path}")
            
            # Add unique events to combined list
            for event in events:
                # Create a key to identify unique events
                key = f"{event.get('title', '')}-{event.get('date', '')}-{event.get('type', '')}"
                
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_events.append(event)
                    
        except Exception as e:
            logger.error(f"Error loading events from {file_path}: {e}")
    
    logger.info(f"Combined {len(all_events)} unique events from all sources")
    
    # Sort events by date
    all_events.sort(key=lambda x: x.get('date', '9999-99-99'))
    
    return all_events

def main():
    """Main function."""
    # Set paths
    script_dir = Path(__file__).parent
    output_dir = Path("data")
    output_file = output_dir / "medical_events.json"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Create temporary directory for individual extraction outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Define our extraction scripts and their temp output files
        extraction_scripts = [
            ("create_events_from_extractions.py", temp_dir_path / "standard_events.json"),
            ("extract_with_ai.py", temp_dir_path / "ai_events.json"),
            ("extract_from_timeline.py", temp_dir_path / "timeline_events.json"),
            ("extract_from_life_story.py", temp_dir_path / "life_story_events.json")
        ]
        
        # Run each extraction script
        all_succeeded = True
        for script_name, temp_output in extraction_scripts:
            if not run_extraction_script(script_name, temp_output):
                logger.warning(f"Failed to run {script_name}")
                all_succeeded = False
        
        # Combine all events from successful extractions
        all_events = combine_events([str(temp_output) for _, temp_output in extraction_scripts])
        
        # Save combined events
        if all_events:
            logger.info(f"Combined {len(all_events)} unique events from all sources")
            if save_events(all_events, output_file):
                logger.info(f"Successfully saved all events to {output_file}")
            else:
                logger.error(f"Failed to save combined events")
                return 1
        else:
            logger.error("No events were extracted from any source")
            return 1
    
    return 0 if all_succeeded else 1

if __name__ == "__main__":
    sys.exit(main()) 