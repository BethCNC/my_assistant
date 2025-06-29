#!/usr/bin/env python3
"""
PDF Processing Example - Medical Data to Notion Integration

This example demonstrates how to process medical PDF documents and extract
structured data for Notion databases.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directories to path for imports
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir.parent.parent))

from notion_integration.medical_data_processor import MedicalDataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pdf_processing")


def process_pdf_document(
    pdf_path: str,
    processor: MedicalDataProcessor,
    document_type: Optional[str] = None,
    document_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a PDF medical document and extract structured data
    
    Args:
        pdf_path: Path to the PDF file
        processor: MedicalDataProcessor instance
        document_type: Type of medical document (optional)
        document_date: Date of document in ISO format (optional)
        
    Returns:
        Dictionary with extracted entities
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return {"error": "File not found"}
    
    # Infer document type and date if not provided
    if not document_type:
        document_type = infer_document_type(pdf_path)
    
    if not document_date:
        document_date = infer_document_date(pdf_path)
    
    # Process the PDF document
    logger.info(f"Processing PDF: {pdf_path}")
    logger.info(f"Document type: {document_type}")
    logger.info(f"Document date: {document_date}")
    
    try:
        # For demonstration purposes, we'll extract text from PDF manually
        # In a real implementation, MedicalDataProcessor would handle this
        from PyPDF2 import PdfReader
        
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Now process the extracted text
        result = processor.process_document(
            text=text,
            document_type=document_type,
            document_date=document_date,
            file_path=pdf_path
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return {"error": str(e)}


def infer_document_type(file_path: str) -> str:
    """
    Infer document type from file name or path
    
    Args:
        file_path: Path to the document
        
    Returns:
        Inferred document type
    """
    lower_path = file_path.lower()
    file_name = os.path.basename(lower_path)
    
    if any(term in lower_path for term in ["lab", "test", "result", "panel"]):
        return "lab_result"
    elif any(term in lower_path for term in ["visit", "appointment", "note", "consult"]):
        return "clinical_note"
    elif any(term in lower_path for term in ["medication", "prescription", "drug", "med_list"]):
        return "medication_list"
    elif any(term in lower_path for term in ["radiology", "imaging", "xray", "mri", "ct", "ultrasound"]):
        return "imaging_report"
    elif any(term in lower_path for term in ["hospital", "discharge", "admission"]):
        return "hospital_note"
    elif any(term in lower_path for term in ["pathology", "biopsy", "specimen"]):
        return "pathology_report"
    else:
        return "general_medical_document"


def infer_document_date(file_path: str) -> str:
    """
    Try to infer document date from file name using common patterns
    
    Args:
        file_path: Path to the document
        
    Returns:
        Inferred date in ISO format, or current date if not found
    """
    file_name = os.path.basename(file_path)
    
    # Try common date patterns in file names
    import re
    
    # Try YYYY-MM-DD pattern
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
    if date_match:
        return date_match.group(1)
    
    # Try MM-DD-YYYY pattern
    date_match = re.search(r'(\d{2}-\d{2}-\d{4})', file_name)
    if date_match:
        parts = date_match.group(1).split('-')
        return f"{parts[2]}-{parts[0]}-{parts[1]}"
    
    # Try YYYYMMDD pattern
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', file_name)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    
    # Default to current date if no pattern found
    return datetime.now().strftime("%Y-%m-%d")


def create_sample_pdf():
    """
    Create a sample PDF medical document for demonstration
    
    Returns:
        Path to the created PDF file
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        sample_pdf_path = "sample_medical_report.pdf"
        
        # Create a sample PDF
        c = canvas.Canvas(sample_pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        
        # Add header
        c.drawString(100, 750, "MEDICAL CONSULTATION REPORT")
        c.drawString(100, 735, "Date: 2023-08-15")
        c.drawString(100, 720, "Patient ID: MRN12345678")
        c.drawString(100, 705, "Provider: Dr. Emily Chen, Neurology")
        
        # Add content
        c.drawString(100, 675, "REASON FOR VISIT:")
        c.drawString(120, 660, "Patient presents with recurring headaches and dizziness for the past 3 months.")
        c.drawString(120, 645, "Reports increased frequency in the last 2 weeks.")
        
        c.drawString(100, 615, "HISTORY:")
        c.drawString(120, 600, "- No previous history of migraines")
        c.drawString(120, 585, "- History of mild hypertension, controlled with medication")
        c.drawString(120, 570, "- No recent head trauma or injuries")
        
        c.drawString(100, 540, "CURRENT MEDICATIONS:")
        c.drawString(120, 525, "1. Lisinopril 10mg daily for hypertension")
        c.drawString(120, 510, "2. Acetaminophen 500mg as needed for pain")
        c.drawString(120, 495, "3. Multivitamin daily")
        
        c.drawString(100, 465, "ASSESSMENT:")
        c.drawString(120, 450, "Patient likely experiencing tension headaches with possible")
        c.drawString(120, 435, "vestibular component. No signs of serious neurological issues.")
        
        c.drawString(100, 405, "PLAN:")
        c.drawString(120, 390, "1. MRI of brain to rule out structural abnormalities")
        c.drawString(120, 375, "2. Start Sumatriptan 50mg for acute headache treatment")
        c.drawString(120, 360, "3. Recommend stress reduction techniques and regular sleep schedule")
        c.drawString(120, 345, "4. Follow-up appointment in 3 weeks")
        
        c.drawString(100, 315, "UPCOMING APPOINTMENTS:")
        c.drawString(120, 300, "1. MRI Imaging: August 22, 2023 at 10:30 AM, Radiology Department")
        c.drawString(120, 285, "2. Follow-up: September 5, 2023 at 2:15 PM with Dr. Chen")
        
        c.drawString(100, 240, "Dr. Emily Chen, MD")
        c.drawString(100, 225, "Neurology Department")
        c.drawString(100, 210, "Medical Center")
        
        c.save()
        logger.info(f"Created sample PDF at {sample_pdf_path}")
        return sample_pdf_path
        
    except ImportError:
        logger.error("ReportLab not installed. Cannot create sample PDF.")
        logger.error("Install with: pip install reportlab")
        return None


def main():
    """Main function for PDF processing example"""
    parser = argparse.ArgumentParser(description="Process medical PDF documents")
    parser.add_argument("--pdf", "-p", help="Path to PDF file to process")
    parser.add_argument("--config", "-c", default="notion_config.json", help="Path to configuration file")
    parser.add_argument("--type", "-t", help="Document type (e.g., clinical_note, lab_result)")
    parser.add_argument("--date", "-d", help="Document date in YYYY-MM-DD format")
    parser.add_argument("--create-sample", "-s", action="store_true", help="Create and process a sample PDF")
    args = parser.parse_args()
    
    # Create sample PDF if requested
    if args.create_sample:
        pdf_path = create_sample_pdf()
        if not pdf_path:
            return
    elif args.pdf:
        pdf_path = args.pdf
    else:
        logger.error("Please specify a PDF file with --pdf or use --create-sample")
        return
    
    # Load configuration
    config_path = args.config
    if not os.path.exists(config_path):
        config_path = script_dir / "notion_config.json"
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found at {config_path}")
        logger.error("Please create a configuration file with your API keys and database IDs")
        return
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Create processor instance
    processor = MedicalDataProcessor(config=config)
    
    # Process the PDF
    result = process_pdf_document(
        pdf_path=pdf_path,
        processor=processor,
        document_type=args.type,
        document_date=args.date
    )
    
    # Log results
    if "error" in result:
        logger.error(f"Processing failed: {result['error']}")
        return
    
    logger.info("Processing complete. Results:")
    logger.info(f"Appointments created: {len(result.get('appointments', []))}")
    logger.info(f"Medications created/updated: {len(result.get('medications', []))}")
    logger.info(f"Conditions created/updated: {len(result.get('conditions', []))}")
    logger.info(f"Symptoms created/updated: {len(result.get('symptoms', []))}")
    logger.info(f"Providers created/updated: {len(result.get('providers', []))}")
    
    logger.info("Check your Notion databases to see the created entries.")


if __name__ == "__main__":
    main() 