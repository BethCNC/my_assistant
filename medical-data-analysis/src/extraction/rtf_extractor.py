import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from striprtf.striprtf import rtf_to_text

from src.extraction.base import BaseExtractor


class RTFExtractor(BaseExtractor):
    """Extractor for RTF files (older medical documents, referral letters, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b')
        self.extracted_dates = set()
        
        # For section detection
        self.section_patterns = [
            re.compile(r'(ASSESSMENT|Assessment)[\s:]+([^\n]+)'),
            re.compile(r'(DIAGNOSIS|Diagnosis)[\s:]+([^\n]+)'),
            re.compile(r'(MEDICATIONS|Medications)[\s:]+([^\n]+)'),
            re.compile(r'(TREATMENT|Treatment)[\s:]+([^\n]+)'),
            re.compile(r'(HISTORY|History)[\s:]+([^\n]+)'),
            re.compile(r'(PLAN|Plan)[\s:]+([^\n]+)'),
            re.compile(r'(LAB RESULTS|Lab Results)[\s:]+([^\n]+)')
        ]
        
        # For provider detection
        self.provider_patterns = [
            re.compile(r'([A-Z][a-z]+\s+[A-Z][a-z]+,\s+M\.?D\.?)', re.IGNORECASE),
            re.compile(r'(Dr\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+)', re.IGNORECASE),
            re.compile(r'([A-Z][a-z]+\s+Clinic)', re.IGNORECASE),
            re.compile(r'([A-Z][a-z]+\s+Hospital)', re.IGNORECASE)
        ]
    
    def _extract_metadata(self) -> Dict:
        """Extract metadata from the RTF file."""
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
        metadata["file_type"] = "rtf"
        metadata["file_name"] = self.source_file.name
        
        return metadata
    
    def _extract_content(self) -> str:
        """Extract content from the RTF file using striprtf."""
        try:
            with open(self.source_file, 'r', encoding='utf-8', errors='ignore') as file:
                rtf_content = file.read()
                
                # Convert RTF to plain text
                plain_text = rtf_to_text(rtf_content)
                
                # Set confidence score based on content length
                content_len = len(plain_text)
                if content_len > 100:
                    self.confidence_score = 1.0
                elif content_len > 10:
                    self.confidence_score = 0.8
                else:
                    self.confidence_score = 0.5
                    
                return plain_text
                
        except Exception as e:
            self.confidence_score = 0.0
            return f"Error extracting content: {str(e)}"
    
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
        """Extract medical sections from the RTF content."""
        sections = {}
        
        if not self.content:
            return sections
        
        # Apply each section pattern
        for pattern in self.section_patterns:
            matches = pattern.findall(self.content)
            for match in matches:
                if len(match) >= 2:
                    section_name = match[0].strip()
                    section_content = match[1].strip()
                    sections[section_name] = section_content
        
        # Look for sections based on common header formats
        lines = self.content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line looks like a section header
            if line.isupper() and len(line) < 30:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                    
                # Start new section
                current_section = line
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Save the last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
            
        return sections
    
    def extract_providers(self) -> List[str]:
        """Extract healthcare provider names or organizations."""
        providers = set()
        
        if not self.content:
            return list(providers)
        
        # Apply each provider pattern
        for pattern in self.provider_patterns:
            matches = pattern.findall(self.content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                providers.add(match.strip())
        
        return list(providers)
    
    def extract_phone_numbers(self) -> List[str]:
        """Extract phone numbers from the document."""
        if not self.content:
            return []
            
        # Pattern for US phone numbers
        phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        matches = phone_pattern.findall(self.content)
        
        return matches
    
    def extract_patient_info(self) -> Dict[str, str]:
        """Attempt to extract patient information."""
        info = {}
        
        if not self.content:
            return info
            
        # Look for common patient info patterns
        name_pattern = re.compile(r'(?:Patient\s*Name|Name)[\s:]+([^\n]+)', re.IGNORECASE)
        dob_pattern = re.compile(r'(?:Date\s*of\s*Birth|DOB|Birth\s*Date)[\s:]+([^\n]+)', re.IGNORECASE)
        mrn_pattern = re.compile(r'(?:Medical\s*Record\s*Number|MRN|Record\s*Number)[\s:]+([^\n]+)', re.IGNORECASE)
        
        # Extract matches
        name_match = name_pattern.search(self.content)
        if name_match:
            info["patient_name"] = name_match.group(1).strip()
            
        dob_match = dob_pattern.search(self.content)
        if dob_match:
            info["date_of_birth"] = dob_match.group(1).strip()
            
        mrn_match = mrn_pattern.search(self.content)
        if mrn_match:
            info["medical_record_number"] = mrn_match.group(1).strip()
            
        return info 