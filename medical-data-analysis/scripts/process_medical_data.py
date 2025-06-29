#!/usr/bin/env python3
"""
Medical Data Processing Script

This script processes all medical data files in the input directory,
extracts relevant information, and saves the results.
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
import concurrent.futures
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("processed_data/extraction_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Custom JSON encoder for serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

def process_file(file_path: Path) -> Dict[str, Any]:
    """
    Process a single medical file and extract information.
    
    Args:
        file_path: Path to the file to process
        
    Returns:
        Dictionary with extraction results
    """
    try:
        # Import the factory module and get the appropriate extractor
        from src.extraction.factory import get_extractor
        from src.ai.model_integration import ModelIntegration
        
        logger.info(f"Processing file: {file_path}")
        extractor = get_extractor(file_path)
        if not extractor:
            logger.warning(f"No suitable extractor found for file: {file_path}")
            return {"error": "No suitable extractor found", "file": str(file_path)}
        
        # Process the file
        extraction_result = extractor.process_file(file_path)
        
        # Perform AI analysis on the content
        ai_model = ModelIntegration()
        ai_analysis = ai_model.process(extraction_result)
        extraction_result['ai_analysis'] = ai_analysis
        
        # Save result to JSON (without the full content to save space)
        output_path = Path(f"processed_data/extracted/{file_path.stem}_extraction.json")
        os.makedirs(output_path.parent, exist_ok=True)
        
        result_without_content = {k: v for k, v in extraction_result.items() if k != 'content'}
        result_without_content['content_length'] = len(extraction_result.get('content', ''))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_without_content, f, indent=2, cls=CustomJSONEncoder)
            
        # Return summary
        entity_counts = {}
        if 'ai_analysis' in extraction_result and 'entities' in extraction_result['ai_analysis']:
            entities = extraction_result['ai_analysis']['entities']
            for entity_type, entity_list in entities.items():
                entity_counts[entity_type] = len(entity_list)
        
        return {
            "file": str(file_path),
            "extractor": extractor.__class__.__name__,
            "confidence": extraction_result.get('confidence_score', 0),
            "output_path": str(output_path),
            "extracted_entities": {
                "dates": len(extraction_result.get('extracted_dates', [])),
                "providers": len(extraction_result.get('providers', [])),
                **entity_counts
            },
            "ai_processing": "success" if 'ai_analysis' in extraction_result else "not performed"
        }
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "file": str(file_path)}

def find_medical_files(input_dir: Path) -> List[Path]:
    """
    Find all medical files in the input directory.
    
    Args:
        input_dir: Directory to search for files
        
    Returns:
        List of file paths
    """
    medical_files = []
    
    # Check if the input directory exists
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"Input directory does not exist: {input_dir}")
        return []
    
    # Walk through the directory and find files
    for root, _, files in os.walk(input_dir):
        for file in files:
            # Skip hidden files and directories
            if file.startswith('.') or '__pycache__' in root:
                continue
                
            file_path = Path(root) / file
            
            # Skip directories and empty files
            if not file_path.is_file() or file_path.stat().st_size == 0:
                continue
                
            # Only include files with appropriate extensions
            if file_path.suffix.lower() in ['.txt', '.pdf', '.csv', '.html', '.htm', '.md', '.rtf', '.docx']:
                medical_files.append(file_path)
    
    return medical_files

def main():
    """Main function to process all medical files."""
    # Create output directories
    os.makedirs("processed_data/extracted", exist_ok=True)
    os.makedirs("processed_data/summaries", exist_ok=True)
    
    # Find all medical files
    input_dir = Path("input")
    medical_files = find_medical_files(input_dir)
    logger.info(f"Found {len(medical_files)} medical files to process")
    
    # Process all files in parallel
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in medical_files}
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(f"Completed processing {file}")
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
                results.append({"error": str(e), "file": str(file)})
    
    # Save overall summary
    summary = {
        "total_files": len(medical_files),
        "successful": len([r for r in results if "error" not in r]),
        "failed": len([r for r in results if "error" in r]),
        "processing_date": datetime.now().isoformat(),
        "file_results": results
    }
    
    with open("processed_data/extraction_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, cls=CustomJSONEncoder)
    
    logger.info(f"Processing complete. {summary['successful']} files processed successfully, {summary['failed']} failed.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 