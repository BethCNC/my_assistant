import hashlib
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Any
import re
import logging

import pandas as pd

from src.config import settings


class BaseExtractor(ABC):
    """Base class for all document extractors. Defines the common interface and utility methods."""
    
    def __init__(self):
        """Initialize the extractor with common attributes."""
        self.source_file = None
        self.metadata = {}
        self.content = ""
        self.extracted_date = datetime.now().isoformat()
        self.file_hash = None
        self.confidence_score = 0.0
        
        # Common patterns for doctors
        self.doctor_pattern = re.compile(
            r'\b(?:Dr\.|Doctor|MD|DO|physician|provider)\s*([A-Z][a-z]+\s+(?:[A-Z][a-z]*\s+)?[A-Z][a-z]+)',
            re.IGNORECASE
        )
        
        # Common date patterns
        self.date_pattern = re.compile(
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
        )
        
        # Appointment date indicators
        self.appointment_indicators = [
            r'appointment date', r'date of visit', r'visit date', 
            r'date of appointment', r'date of service', r'seen on',
            r'encounter date', r'date seen'
        ]
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_file(self, file_path: Union[str, Path]) -> Dict:
        """
        Process a file and extract its contents and metadata.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dict containing extracted content and metadata
        """
        self.source_file = Path(file_path)
        self.file_hash = self._calculate_file_hash()
        self.metadata = self._extract_metadata()
        self.content = self._extract_content()
        
        # Compile results
        results = {
            "source_file": str(self.source_file),
            "file_hash": self.file_hash,
            "metadata": self.metadata,
            "content": self.content,
            "extraction_date": self.extracted_date,
            "confidence_score": self.confidence_score,
            "extracted_dates": self.extract_dates(),
            "appointment_dates": self.extract_appointment_dates(),
            "providers": self.extract_providers()
        }
        
        return results
    
    def _calculate_file_hash(self) -> str:
        """Calculate SHA-256 hash of the file for deduplication and validation."""
        if not self.source_file.exists():
            raise FileNotFoundError(f"File not found: {self.source_file}")
        
        sha256_hash = hashlib.sha256()
        with open(self.source_file, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _extract_date_from_filename(self) -> Optional[str]:
        """
        Extract date from filename if it matches common date patterns.
        
        Returns:
            ISO formatted date string if found, None otherwise
        """
        if not self.source_file:
            return None
            
        filename = self.source_file.stem
        
        # Look for date patterns in filename
        date_matches = re.findall(r'(\d{4}[-_/]\d{1,2}[-_/]\d{1,2}|\d{1,2}[-_/]\d{1,2}[-_/]\d{4})', filename)
        
        if date_matches:
            date_str = date_matches[0]
            # Convert to standard format
            date_str = date_str.replace('_', '-').replace('/', '-')
            
            # Determine format and parse
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                # YYYY-MM-DD
                year, month, day = date_str.split('-')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', date_str):
                # MM-DD-YYYY or DD-MM-YYYY (assume MM-DD-YYYY for US format)
                month, day, year = date_str.split('-')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
        return None
    
    @abstractmethod
    def _extract_metadata(self) -> Dict:
        """
        Extract metadata from the file.
        Must be implemented by each extractor subclass.
        """
        pass
    
    @abstractmethod
    def _extract_content(self) -> str:
        """
        Extract content from the file.
        Must be implemented by each extractor subclass.
        """
        pass
    
    def save_to_processed(self, content: Optional[str] = None) -> Path:
        """
        Save the processed content to the processed directory.
        
        Args:
            content: Optional content to save (uses self.content if None)
            
        Returns:
            Path to the saved file
        """
        if content is None:
            content = self.content
            
        if not content:
            raise ValueError("No content to save")
        
        # Create directory if it doesn't exist
        file_type = self.source_file.suffix.replace(".", "")
        target_dir = settings.PROCESSED_DIR / file_type
        os.makedirs(target_dir, exist_ok=True)
        
        # Save with original filename but in the processed directory
        target_file = target_dir / self.source_file.name
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        return target_file
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert extraction results to a DataFrame for analysis."""
        data = {
            "source_file": [str(self.source_file)],
            "file_hash": [self.file_hash],
            "extraction_date": [self.extracted_date],
            "confidence_score": [self.confidence_score]
        }
        
        # Add metadata to the dataframe
        for key, value in self.metadata.items():
            data[f"metadata_{key}"] = [value]
        
        # Add truncated content for preview
        content_preview = self.content[:1000] + "..." if len(self.content) > 1000 else self.content
        data["content_preview"] = [content_preview]
        
        return pd.DataFrame(data)
    
    def extract_dates(self) -> Set[str]:
        """
        Extract all dates mentioned in the content.
        
        Returns:
            Set of date strings
        """
        dates = set()
        
        if not self.content:
            return dates
            
        # Extract dates using pattern
        matches = self.date_pattern.findall(self.content)
        
        for date_str in matches:
            # Try to normalize format
            try:
                if '/' in date_str:
                    parts = date_str.split('/')
                elif '-' in date_str:
                    parts = date_str.split('-')
                else:
                    continue
                    
                # Handle different formats
                if len(parts) == 3:
                    if len(parts[2]) == 4:  # MM/DD/YYYY
                        month, day, year = parts
                    elif len(parts[0]) == 4:  # YYYY/MM/DD
                        year, month, day = parts
                    else:  # Ambiguous, assume MM/DD/YY
                        month, day, year = parts
                        
                    # Ensure 4-digit year
                    if len(year) == 2:
                        if int(year) > 50:  # Assume 19xx for years > 50
                            year = f"19{year}"
                        else:  # Assume 20xx for years <= 50
                            year = f"20{year}"
                            
                    normalized_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    dates.add(normalized_date)
            except:
                # If parsing fails, add the original string
                dates.add(date_str)
                
        return dates
        
    def extract_providers(self) -> List[Dict[str, Any]]:
        """Extract healthcare provider names from the content.
        
        Returns:
            List of dictionaries with provider information
        """
        providers = []
        
        if not self.content:
            return providers
            
        for match in self.doctor_pattern.finditer(self.content):
            provider_name = match.group(1).strip()
            
            # Get some context around the name
            start = max(0, match.start() - 30)
            end = min(len(self.content), match.end() + 30)
            context = self.content[start:end]
            
            # Check if this looks like a real provider reference 
            # (not just someone with Dr. in their name)
            if re.search(r'\b(appointment|visit|consult|referred|prescribed|diagnosed|examination|clinic|hospital)\b', 
                         context, re.IGNORECASE):
                providers.append({
                    "name": provider_name,
                    "context": context.strip(),
                    "position": match.start()
                })
                
        return providers
        
    def extract_appointment_dates(self) -> List[Dict[str, Any]]:
        """Extract dates that appear to be appointment dates.
        
        Returns:
            List of dictionaries with appointment date information
        """
        appointment_dates = []
        
        if not self.content:
            return appointment_dates
            
        # Create pattern for appointment date indicators
        indicator_pattern = re.compile(
            '|'.join(self.appointment_indicators),
            re.IGNORECASE
        )
        
        # Find all instances of appointment indicators
        for match in indicator_pattern.finditer(self.content):
            # Look for a date near this indicator (within 50 chars)
            start = max(0, match.start() - 20)
            end = min(len(self.content), match.end() + 30)
            context = self.content[start:end]
            
            # Extract dates from this context
            date_matches = self.date_pattern.findall(context)
            
            for date_str in date_matches:
                try:
                    # Normalize the date
                    if '/' in date_str:
                        parts = date_str.split('/')
                    elif '-' in date_str:
                        parts = date_str.split('-')
                    else:
                        continue
                        
                    # Handle different formats
                    if len(parts) == 3:
                        if len(parts[2]) == 4:  # MM/DD/YYYY
                            month, day, year = parts
                        elif len(parts[0]) == 4:  # YYYY/MM/DD
                            year, month, day = parts
                        else:  # Ambiguous, assume MM/DD/YY
                            month, day, year = parts
                            
                        # Ensure 4-digit year
                        if len(year) == 2:
                            if int(year) > 50:
                                year = f"19{year}"
                            else:
                                year = f"20{year}"
                                
                        normalized_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        
                        appointment_dates.append({
                            "date": normalized_date,
                            "indicator": match.group(0),
                            "context": context.strip()
                        })
                except:
                    continue
                    
        # If we found no clear appointment dates, use the most prominent date in the document
        if not appointment_dates and self.metadata.get("file_date"):
            appointment_dates.append({
                "date": self.metadata["file_date"],
                "indicator": "inferred from document",
                "context": "Document date used as appointment date"
            })
            
        return appointment_dates 