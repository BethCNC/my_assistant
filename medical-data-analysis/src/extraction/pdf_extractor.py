import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.pdfparser import PDFSyntaxError

from src.extraction.base import BaseExtractor


class PDFExtractor(BaseExtractor):
    """Extractor for PDF files (medical records, lab reports, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.total_pages = 0
        self.extracted_pages = []
        self.page_texts = []
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b')
        self.extracted_dates = set()
        self.medical_terms = set([
            "diagnosis", "assessment", "medication", "prescription", "doctor", "physician",
            "treatment", "therapy", "symptom", "report", "result", "lab", "test", "condition",
            "referral", "specialist", "consultation", "visit", "hospital", "clinic", "patient",
            "MRI", "CT scan", "X-ray", "blood test", "urine test"
        ])
        
        # For section detection
        self.section_patterns = [
            re.compile(r'(ASSESSMENT|Assessment)[\\s:]+([^\\n]+)'),
            re.compile(r'(DIAGNOSIS|Diagnosis)[\\s:]+([^\\n]+)'),
            re.compile(r'(MEDICATIONS|Medications)[\\s:]+([^\\n]+)'),
            re.compile(r'(ALLERGIES|Allergies)[\\s:]+([^\\n]+)'),
            re.compile(r'(HISTORY|History)[\\s:]+([^\\n]+)'),
            re.compile(r'(PHYSICAL EXAMINATION|Physical Examination)[\\s:]+([^\\n]+)'),
            re.compile(r'(LABS|Labs|LABORATORY|Laboratory)[\\s:]+([^\\n]+)'),
            re.compile(r'(PLAN|Plan)[\\s:]+([^\\n]+)')
        ]
        
        self.pdf_parser = None
    
    def _extract_metadata(self) -> Dict:
        """Extract metadata from the PDF file."""
        metadata = {}
        
        # Extract date from filename
        file_date = self._extract_date_from_filename()
        if file_date:
            metadata["file_date"] = file_date
        
        # Get file creation and modification times
        stat = self.source_file.stat()
        metadata["creation_time"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        metadata["modification_time"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Basic file properties
        metadata["file_size"] = stat.st_size
        metadata["file_type"] = "pdf"
        metadata["file_name"] = self.source_file.name
        
        # Try to extract PDF-specific metadata
        try:
            with open(self.source_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.total_pages = len(pdf_reader.pages)
                metadata["page_count"] = self.total_pages
                
                # Try to get PDF document info
                pdf_info = pdf_reader.metadata
                if pdf_info:
                    if pdf_info.title:
                        metadata["title"] = pdf_info.title
                    if pdf_info.author:
                        metadata["author"] = pdf_info.author
                    if pdf_info.subject:
                        metadata["subject"] = pdf_info.subject
                    if pdf_info.creator:
                        metadata["creator"] = pdf_info.creator
                    if pdf_info.producer:
                        metadata["producer"] = pdf_info.producer
                    if pdf_info.creation_date:
                        metadata["pdf_creation_date"] = pdf_info.creation_date
        except Exception as e:
            metadata["extraction_error"] = str(e)
            
        return metadata
    
    def _extract_content(self) -> str:
        """
        Extract text content from the PDF file.
        Uses PyPDF2 first, and falls back to pdfminer.six for better text extraction if needed.
        """
        content = ""
        self.page_texts = []
        
        try:
            # First attempt with PyPDF2
            with open(self.source_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.total_pages = len(pdf_reader.pages)
                
                for i in range(self.total_pages):
                    try:
                        page = pdf_reader.pages[i]
                        page_text = page.extract_text()
                        
                        if page_text.strip():  # If text was extracted successfully
                            self.page_texts.append(page_text)
                            self.extracted_pages.append(i)
                        else:
                            # If PyPDF2 fails to extract text from this page, make a note
                            self.page_texts.append(f"[Failed to extract text from page {i+1}]")
                    except Exception as e:
                        self.page_texts.append(f"[Error extracting page {i+1}: {str(e)}]")
                
                content = "\n===== PAGE BREAK =====\n".join(self.page_texts)
                
                # If PyPDF2 failed to extract meaningful text, try pdfminer
                if not content.strip() or "[Failed to extract text" in content:
                    content = self._extract_with_pdfminer()
        except Exception as e:
            # If PyPDF2 fails completely, try pdfminer
            content = self._extract_with_pdfminer()
            if not content:
                content = f"Error extracting content: {str(e)}"
                self.confidence_score = 0.0
                return content
        
        # Set confidence score based on extraction results
        if len(self.extracted_pages) == self.total_pages and self.total_pages > 0:
            self.confidence_score = 1.0
        elif len(self.extracted_pages) > 0:
            self.confidence_score = len(self.extracted_pages) / self.total_pages
        else:
            self.confidence_score = 0.3  # Some text was extracted but not pages
            
        return content
    
    def _extract_with_pdfminer(self) -> str:
        """Fallback extraction method using pdfminer.six."""
        try:
            content = pdfminer_extract_text(self.source_file)
            if content.strip():
                self.confidence_score = 0.8  # Good extraction but using fallback
                return content
            else:
                return "[Failed to extract any text content with pdfminer]"
        except PDFSyntaxError:
            return "[PDF syntax error - possibly corrupted or encrypted file]"
        except Exception as e:
            return f"[Error with pdfminer extraction: {str(e)}]"
            
    def extract_dates(self) -> Set[str]:
        """Extract all dates mentioned in the text content."""
        if not self.content:
            return set()
            
        date_matches = self.date_pattern.findall(self.content)
        normalized_dates = set()
        
        for date_str in date_matches:
            try:
                # Try to parse and normalize the date
                if '/' in date_str:
                    parts = date_str.split('/')
                elif '-' in date_str:
                    parts = date_str.split('-')
                else:
                    continue
                    
                # Handle different date formats
                if len(parts) == 3:
                    if len(parts[2]) == 4:  # MM/DD/YYYY
                        month, day, year = parts
                    else:  # YYYY/MM/DD
                        year, month, day = parts
                        
                    # Make sure year is 4 digits
                    if len(year) == 2:
                        if int(year) > 50:  # Assume 19xx for years > 50
                            year = f"19{year}"
                        else:  # Assume 20xx for years <= 50
                            year = f"20{year}"
                            
                    normalized_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    normalized_dates.add(normalized_date)
            except:
                continue
                
        self.extracted_dates = normalized_dates
        return normalized_dates
    
    def extract_sections(self) -> Dict[str, str]:
        """Extract common medical report sections."""
        if not self.content:
            return {}
            
        sections = {}
        for pattern in self.section_patterns:
            matches = pattern.findall(self.content)
            for match in matches:
                if len(match) >= 2:
                    section_name = match[0].strip()
                    section_content = match[1].strip()
                    sections[section_name] = section_content
                    
        return sections
    
    def extract_providers(self) -> List[str]:
        """Extract healthcare provider names if present."""
        if not self.content:
            return []
            
        providers = []
        # Look for common doctor name patterns: Dr. LastName or FirstName LastName, MD
        dr_pattern = re.compile(r'Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)')
        md_pattern = re.compile(r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(?:M\.?D\.?|D\.?O\.?)')
        
        dr_matches = dr_pattern.findall(self.content)
        md_matches = md_pattern.findall(self.content)
        
        providers.extend(dr_matches)
        providers.extend(md_matches)
        
        return list(set(providers))
    
    def detect_document_type(self) -> str:
        """Attempt to detect the type of medical document."""
        if not self.content:
            return "unknown"
        
        content_lower = self.content.lower()
        
        # Look for specific markers in the text
        if "lab" in content_lower and "result" in content_lower:
            return "lab_report"
        elif "radiology" in content_lower or "imaging" in content_lower or "x-ray" in content_lower:
            return "imaging_report"
        elif "assessment" in content_lower and "plan" in content_lower:
            return "clinical_note"
        elif "prescription" in content_lower or "rx" in content_lower:
            return "prescription"
        elif "discharge" in content_lower and "summary" in content_lower:
            return "discharge_summary"
        elif "referral" in content_lower:
            return "referral"
        elif "progress" in content_lower and "note" in content_lower:
            return "progress_note"
        elif "history" in content_lower and "physical" in content_lower:
            return "history_physical"
        
        # Default to general medical document
        return "medical_document"
    
    def extract_medical_providers(self) -> List[str]:
        """Extract potential healthcare provider names or organizations."""
        if not self.content:
            return []
        
        providers = set()
        
        # Apply each pattern
        for pattern in self.section_patterns:
            matches = pattern.findall(self.content)
            for match in matches:
                providers.add(match[1].strip())
        
        return list(providers)
    
    def extract_page_range(self, start_page: int, end_page: int) -> str:
        """Extract text content from a specific range of pages."""
        if not self.page_texts or start_page < 0 or end_page >= len(self.page_texts):
            return ""
        
        result = ""
        for i in range(start_page, end_page + 1):
            if i < len(self.page_texts):
                result += f"\n--- Page {i+1} ---\n{self.page_texts[i]}"
        
        return result
    
    def detect_medical_terms(self) -> Dict[str, int]:
        """Detect common medical terms and their frequencies in the document."""
        if not self.content:
            return {}
        
        term_counts = {}
        content_lower = self.content.lower()
        
        for term in self.medical_terms:
            count = content_lower.count(term)
            if count > 0:
                term_counts[term] = count
                
        return term_counts
    
    def extract_images(self) -> List[Dict[str, Any]]:
        """
        Extract images from the PDF file.
        
        Returns:
            List of dictionaries with image data and metadata
        """
        if not self.source_file or not self.source_file.exists():
            return []
        
        # This is just a stub - in a real implementation, you would use
        # a PDF library like PyMuPDF to extract images
        return []
    
    def extract(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract content and metadata from a PDF file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self.process_file(file_path) 