#!/usr/bin/env python3
# Lab Results Parser
# Uses OpenAI API to extract structured information from medical lab results

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import re
import time
from pathlib import Path
from dotenv import load_dotenv

# Try to import OpenAI library
try:
    import openai
    from openai import OpenAI
    HAVE_OPENAI = True
except ImportError:
    HAVE_OPENAI = False


# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def check_dependencies() -> None:
    """Check if required dependencies are installed"""
    missing = []
    
    if not HAVE_OPENAI:
        missing.append("openai")
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Please install required packages:")
        print("  pip install openai python-dotenv")
        sys.exit(1)


def create_openai_client() -> Optional[Any]:
    """Create and configure OpenAI client"""
    if not HAVE_OPENAI:
        return None
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables. "
                        "Please set it in a .env file or environment.")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    return client


def parse_lab_results(text: str, client: Optional[Any] = None) -> Dict[str, Any]:
    """
    Parse lab results text using OpenAI API
    
    Args:
        text: Lab results text content
        client: OpenAI client or None to create new client
        
    Returns:
        Structured lab results data
    """
    if not client:
        client = create_openai_client()
    
    # If text is too long, truncate it to avoid token limits
    # GPT-4 has a context window of ~8k tokens, which is roughly 32k characters
    max_chars = 30000
    if len(text) > max_chars:
        print(f"Warning: Text is too long ({len(text)} chars), truncating to {max_chars} chars")
        text = text[:max_chars]
    
    # Create prompt for lab results parsing
    system_prompt = """
    You are a medical data extraction assistant. Your task is to extract structured information from lab results text. 
    Extract the following information in JSON format:
    
    1. Basic Information:
       - Test Name
       - Collection Date 
       - Report Date
       - Patient Information (name, DOB, ID)
       - Ordering Provider
       - Performing Lab
    
    2. Results:
       For each test result, extract:
       - Test Name
       - Result Value
       - Units
       - Reference Range
       - Flag (abnormal indicators like 'H', 'L', '*' etc.)
       - If flagged as abnormal, indicate this in a boolean field
    
    3. Notes:
       - Any interpretation or notes included with results
       - Any recommendations from the provider
    
    Format your response as a valid JSON object. Use null for missing values.
    If you're uncertain about some information, use the field "uncertain_fields" to list what you're unsure about.
    """
    
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for best accuracy
            temperature=0.2,  # Low temperature for more deterministic outputs
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the JSON response
        result_text = response.choices[0].message.content
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print("Raw response:")
            print(result_text)
            raise
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Return minimal structure with error info
        return {
            "error": str(e),
            "partial_text": text[:200] + "..." if len(text) > 200 else text
        }


def process_lab_file(file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a single lab results text file
    
    Args:
        file_path: Path to the text file containing lab results
        output_dir: Directory to save parsed results
        
    Returns:
        Parsed lab results data
    """
    # Ensure file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the lab results text file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Create OpenAI client
    client = create_openai_client()
    
    # Parse lab results
    result = parse_lab_results(text, client)
    
    # Save parsed results if output directory specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(file_path)
        json_filename = os.path.splitext(base_name)[0] + ".json"
        json_path = os.path.join(output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"  Saved parsed results to {json_path}")
    
    return result


def process_directory(input_dir: str, output_dir: Optional[str] = None,
                     recursive: bool = False) -> List[Dict[str, Any]]:
    """
    Process all text files in a directory
    
    Args:
        input_dir: Directory containing text files with lab results
        output_dir: Directory to save parsed results
        recursive: Whether to search subdirectories
        
    Returns:
        List of parsed lab results data
    """
    results = []
    
    # Get list of text files to process
    if recursive:
        txt_paths = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.txt'):
                    txt_paths.append(os.path.join(root, file))
    else:
        txt_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                    if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith('.txt')]
    
    # Process each text file
    for txt_path in txt_paths:
        try:
            print(f"Processing {os.path.basename(txt_path)}...")
            result = process_lab_file(txt_path, output_dir)
            results.append(result)
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing {txt_path}: {e}")
    
    print(f"Processed {len(results)} text files")
    return results


def main():
    """Main function to run when script is executed directly"""
    parser = argparse.ArgumentParser(description='Parse lab results text files using OpenAI')
    parser.add_argument('input', help='Input text file or directory to process')
    parser.add_argument('--output-dir', '-o', help='Directory to save parsed results')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Recursively process directories')
    
    args = parser.parse_args()
    
    # Check if required dependencies are installed
    check_dependencies()
    
    input_path = args.input
    
    if os.path.isfile(input_path) and input_path.lower().endswith('.txt'):
        # Process single text file
        process_lab_file(input_path, args.output_dir)
    elif os.path.isdir(input_path):
        # Process directory of text files
        process_directory(input_path, args.output_dir, args.recursive)
    else:
        print(f"Error: {input_path} is not a valid text file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main() 