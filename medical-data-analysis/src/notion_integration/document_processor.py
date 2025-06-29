"""
Document Processor

This module handles processing of various document formats to extract content and metadata.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import re
import mimetypes

class DocumentProcessor:
    """Processes documents of various formats to extract content and metadata"""
    
    def __init__(self):
        """Initialize the document processor"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize supported MIME types
        mimetypes.init()
        
        # Register additional MIME types if needed
        if not mimetypes.guess_type("file.md")[0]:
            mimetypes.add_type("text/markdown", ".md")
    
    def get_document_summary(self, document_path: str) -> Dict[str, Any]:
        """
        Get a summary of a document
        
        Args:
            document_path: Path to the document
            
        Returns:
            Dictionary with document metadata and content
        """
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
            
        # Extract document metadata
        doc_metadata = self._extract_document_metadata(document_path)
        
        # Extract document content
        content = self._extract_document_content(document_path)
        
        # Create document summary
        document_summary = {
            "metadata": doc_metadata,
            "content": content
        }
        
        # Extract additional metadata from content if possible
        content_metadata = self._extract_metadata_from_content(content)
        if content_metadata:
            document_summary["metadata"].update(content_metadata)
        
        return document_summary
    
    def _extract_document_metadata(self, document_path: str) -> Dict[str, Any]:
        """Extract metadata from document file properties"""
        filename = os.path.basename(document_path)
        file_ext = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(document_path)
        modification_time = os.path.getmtime(document_path)
        
        # Try to determine document type by extension and mime type
        mime_type = mimetypes.guess_type(document_path)[0] or "application/octet-stream"
        doc_type = self._determine_document_type(filename, mime_type)
        
        # Try to extract date from filename (e.g., 2023-04-15_visit.txt)
        doc_date = self._extract_date_from_filename(filename)
        
        metadata = {
            "filename": filename,
            "extension": file_ext,
            "mime_type": mime_type,
            "file_size": file_size,
            "modification_time": datetime.fromtimestamp(modification_time).isoformat(),
            "creation_time": None  # May not be available on all platforms
        }
        
        if doc_type:
            metadata["document_type"] = doc_type
        
        if doc_date:
            metadata["document_date"] = doc_date
            
        return metadata
    
    def _determine_document_type(self, filename: str, mime_type: str) -> Optional[str]:
        """Determine document type from filename and MIME type"""
        # Extract from filename pattern (e.g., visit_summary.txt -> visit)
        name_parts = os.path.splitext(filename)[0].split("_")
        if len(name_parts) > 1:
            potential_types = ["visit", "lab", "imaging", "prescription", "referral", "notes"]
            for part in name_parts:
                if part.lower() in potential_types:
                    return part.lower()
        
        # Determine from MIME type
        if mime_type.startswith("text/"):
            return "notes"
        elif mime_type == "application/pdf":
            return "report"
        
        return None
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from filename"""
        # Look for date patterns in filename
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",  # ISO format: 2023-04-15
            r"(\d{8})",              # Compact: 20230415
            r"(\d{2}-\d{2}-\d{4})"   # US format: 04-15-2023
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                
                # Convert to ISO format
                try:
                    if len(date_str) == 8:  # Compact format
                        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    elif "-" in date_str and len(date_str) == 10:  # ISO or similar
                        parts = date_str.split("-")
                        if len(parts[0]) == 4:  # ISO format
                            return date_str
                        else:  # MM-DD-YYYY format
                            return f"{parts[2]}-{parts[0]}-{parts[1]}"
                except Exception as e:
                    self.logger.warning(f"Error parsing date from filename: {e}")
            
        return None
    
    def _extract_document_content(self, document_path: str) -> str:
        """
        Extract content from document
        
        Currently supports:
        - Plain text (.txt)
        - Markdown (.md)
        - HTML (basic, .html)
        - CSV (as text, .csv)
        """
        file_ext = os.path.splitext(document_path)[1].lower()
        
        try:
            # Text-based formats
            if file_ext in [".txt", ".md", ".csv"]:
                with open(document_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            # HTML - simple extraction
            elif file_ext == ".html":
                with open(document_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    # Very basic HTML to text conversion
                    # Remove HTML tags and decode entities (this is simplistic)
                    return re.sub(r'<[^>]+>', ' ', html_content)
                    
            # PDF would require pdfminer.six or similar 
            # Implementation placeholder:
            elif file_ext == ".pdf":
                self.logger.warning("PDF extraction not implemented yet. Install pdfminer.six for PDF support.")
                return "[PDF content not extracted - pdfminer.six required]"
                
            # Unsupported format
            else:
                self.logger.warning(f"Unsupported document format: {file_ext}")
                return f"[Content extraction not supported for {file_ext} format]"
                
        except Exception as e:
            self.logger.error(f"Error extracting content from {document_path}: {str(e)}")
            return f"[Error extracting content: {str(e)}]"
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """Extract metadata from document content"""
        metadata = {}
        
        # Look for date patterns in content
        date_pattern = r"\b(?:Date|DATE|date):\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2}, \d{4})\b"
        date_match = re.search(date_pattern, content)
        if date_match:
            date_str = date_match.group(1)
            # Convert to ISO format (simplistic approach)
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 3:
                    # Assume MM/DD/YYYY format
                    metadata["document_date"] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            elif "-" in date_str and len(date_str.split("-")[0]) == 4:
                # Already ISO format
                metadata["document_date"] = date_str
        
        # Look for provider/doctor name
        provider_pattern = r"\b(?:Provider|Doctor|Dr\.|Physician|PROVIDER):\s*([^,\n\.]{3,40})"
        provider_match = re.search(provider_pattern, content)
        if provider_match:
            metadata["provider"] = provider_match.group(1).strip()
        
        # Look for document type hints in content
        type_patterns = {
            "visit": r"\b(?:VISIT SUMMARY|Visit Summary|Office Visit|Appointment Summary)\b",
            "lab": r"\b(?:Lab Results|Laboratory Report|Test Results|LABORATORY DATA)\b",
            "imaging": r"\b(?:Imaging Results|Radiology Report|MRI|X-ray|Scan Results)\b",
            "prescription": r"\b(?:Prescription|Rx|Medication Order)\b",
            "referral": r"\b(?:Referral|Referred To)\b"
        }
        
        for doc_type, pattern in type_patterns.items():
            if re.search(pattern, content):
                metadata["document_type"] = doc_type
                break
        
        return metadata 