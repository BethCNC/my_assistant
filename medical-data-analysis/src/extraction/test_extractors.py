#!/usr/bin/env python
import os
from pathlib import Path
import logging
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Add project root to path

from src.extraction.factory import get_extractor


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def test_extractor(file_path, logger):
    """Test an extractor on a given file path."""
    logger.info(f"Testing extraction for: {file_path}")
    
    # Get the appropriate extractor
    extractor = get_extractor(file_path)
    
    if not extractor:
        logger.error(f"No suitable extractor found for {file_path}")
        return
    
    logger.info(f"Using extractor: {extractor.__class__.__name__}")
    
    # Extract content and metadata
    try:
        # Use process_file instead of extract
        extraction_result = extractor.process_file(file_path)
        
        # Log extraction results
        logger.info(f"Confidence score: {extractor.confidence_score}")
        logger.info(f"Metadata: {extractor.metadata}")
        
        # Log content preview
        content_preview = extractor.content[:500] + "..." if len(extractor.content) > 500 else extractor.content
        logger.info(f"Content preview: {content_preview}")
        
        # Log additional extraction results based on extractor type
        try:
            dates = extractor.extract_dates()
            logger.info(f"Dates found: {dates}")
        except (AttributeError, NotImplementedError):
            logger.info("Date extraction not supported for this extractor")
        
        # Try additional extraction methods if available
        try:
            sections = extractor.extract_sections()
            logger.info(f"Sections found: {list(sections.keys())}")
        except (AttributeError, NotImplementedError):
            logger.info("Section extraction not supported for this extractor")
            
        try:
            providers = extractor.extract_providers()
            if providers:
                logger.info(f"Providers found: {providers}")
        except (AttributeError, NotImplementedError):
            logger.info("Provider extraction not supported for this extractor")
    
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")


def main():
    """Main function to test extractors on sample files."""
    logger = setup_logging()
    
    # Create a test directory if it doesn't exist
    test_dir = Path(__file__).parent.parent.parent / "test_data"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test files of different types if they don't exist
    test_files = {
        "test.txt": "This is a test medical document.\nDate: 2023-05-15\nDr. Smith, Cardiology\nDiagnosis: Hypertension\nMedication: Lisinopril 10mg",
        "test.md": "# Medical Report\n\n## Patient Information\n- Name: John Doe\n- DOB: 1980-01-15\n\n## Test Results\n| Test | Result | Normal Range |\n|------|--------|-------------|\n| A1C | 5.7% | 4.0-5.6% |",
        "test.csv": "Date,Symptom,Severity,Duration\n2023-05-01,Headache,5,2h\n2023-05-03,Fatigue,3,All day\n2023-05-05,Dizziness,4,1h",
        "test.html": "<html><head><title>Medical Portal</title></head><body><h1>Lab Results</h1><div>Patient: Jane Doe</div><div>Date: 2023-05-20</div><table><tr><th>Test</th><th>Result</th></tr><tr><td>CBC</td><td>Normal</td></tr></table></body></html>"
    }
    
    # Create test files
    for filename, content in test_files.items():
        file_path = test_dir / filename
        if not file_path.exists():
            with open(file_path, "w") as f:
                f.write(content)
    
    # Test each file
    for filename in test_files.keys():
        file_path = test_dir / filename
        test_extractor(file_path, logger)
        logger.info("=" * 80)  # Separator between files
    
    # Additional instructions for testing PDF, DOCX, and RTF
    logger.info("\nTo test PDF, DOCX, and RTF extractors:")
    logger.info("1. Place sample medical PDF files in the test_data directory")
    logger.info("2. Place sample DOCX medical reports in the test_data directory")
    logger.info("3. Place sample RTF medical documents in the test_data directory")
    logger.info("4. Run this script again to test all file types")


if __name__ == "__main__":
    main() 