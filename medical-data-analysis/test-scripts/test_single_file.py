#!/usr/bin/env python3
"""
Test script to extract data from a single medical file.
This script directly uses the extraction components to test their functionality.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle datetime and other non-serializable objects
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

def test_file_extraction(file_path):
    """Test extraction from a single file."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    logger.info(f"Testing extraction for file: {file_path}")
    
    try:
        # Import the factory module and get the appropriate extractor
        from src.extraction.factory import get_extractor
        
        extractor = get_extractor(file_path)
        if not extractor:
            logger.error(f"No suitable extractor found for file: {file_path}")
            return False
        
        # Process the file
        logger.info(f"Using extractor: {extractor.__class__.__name__}")
        extracted_data = extractor.process_file(file_path)
        
        # Output a summary
        logger.info(f"Extraction completed with confidence score: {extracted_data.get('confidence_score', 0)}")
        
        # Extract some key information
        if 'metadata' in extracted_data:
            logger.info(f"Metadata: {json.dumps(extracted_data['metadata'], indent=2, cls=CustomJSONEncoder)}")
        
        content_preview = extracted_data.get('content', '')[:200] + '...' if len(extracted_data.get('content', '')) > 200 else extracted_data.get('content', '')
        logger.info(f"Content preview: {content_preview}")
        
        # Show extracted dates
        if 'extracted_dates' in extracted_data:
            logger.info(f"Extracted dates: {extracted_data['extracted_dates']}")
        
        # Show extracted providers
        if 'providers' in extracted_data:
            logger.info(f"Extracted providers: {len(extracted_data['providers'])}")
            for provider in extracted_data['providers'][:3]:  # Show first 3
                if isinstance(provider, dict):
                    logger.info(f"  Provider: {provider.get('name')}, Specialty: {provider.get('specialty')}")
                else:
                    logger.info(f"  Provider: {provider}")
        
        # Save to JSON file
        output_file = Path(f"processed_data/{file_path.stem}_extraction.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Remove content field to keep file size manageable
            result_copy = {k: v for k, v in extracted_data.items() if k != 'content'}
            result_copy['content_length'] = len(extracted_data.get('content', ''))
            json.dump(result_copy, f, indent=2, cls=CustomJSONEncoder)
        
        logger.info(f"Extraction results saved to: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_single_file.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = test_file_extraction(file_path)
    
    if success:
        print(f"Extraction completed successfully. See logs for details.")
        sys.exit(0)
    else:
        print(f"Extraction failed. See logs for details.")
        sys.exit(1) 