import re
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union

import pandas as pd

from src.extraction.base import BaseExtractor


class CSVExtractor(BaseExtractor):
    """Extractor for CSV files including symptom tracking and tabular medical data."""
    
    def __init__(self):
        super().__init__()
        self.df = None
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b')
        self.extracted_dates = set()
        
        # Common medical column name patterns
        self.symptom_columns = ['symptom', 'symptoms', 'condition', 'diagnosis', 'issue']
        self.date_columns = ['date', 'day', 'visit_date', 'appointment', 'test_date']
        self.provider_columns = ['doctor', 'provider', 'physician', 'specialist', 'clinician']
        self.severity_columns = ['severity', 'intensity', 'pain_level', 'scale', 'rating']
    
    def extract(self, file_path):
        """
        Extract content from a CSV file.
        
        Args:
            file_path: Path to the file to extract
            
        Returns:
            Dict containing extracted content and metadata
        """
        return self.process_file(file_path)
    
    def _extract_metadata(self) -> Dict:
        """Extract metadata from the CSV file."""
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
        metadata["file_type"] = "csv"
        metadata["file_name"] = self.source_file.name
        
        # Add column names if available
        if self.df is not None:
            metadata["columns"] = self.df.columns.tolist()
            metadata["row_count"] = len(self.df)
            
            # Try to identify what type of medical data this CSV contains
            if any(col.lower() in self.symptom_columns for col in self.df.columns):
                metadata["data_type"] = "symptom_tracking"
            elif "test" in ' '.join(self.df.columns).lower() and "result" in ' '.join(self.df.columns).lower():
                metadata["data_type"] = "lab_results"
            elif any(col.lower() in self.date_columns for col in self.df.columns):
                metadata["data_type"] = "medical_timeline"
            else:
                metadata["data_type"] = "unknown"
        
        return metadata
    
    def _extract_content(self) -> str:
        """Extract content from the CSV file."""
        try:
            # Try to load the CSV using pandas
            self.df = pd.read_csv(self.source_file)
            
            # Set confidence score based on content
            if len(self.df) > 0 and len(self.df.columns) > 0:
                # Check for medical data indicators
                col_text = ' '.join(self.df.columns).lower()
                if any(term in col_text for term in 
                       self.symptom_columns + self.date_columns + 
                       self.provider_columns + self.severity_columns):
                    self.confidence_score = 1.0
                else:
                    self.confidence_score = 0.8
            else:
                self.confidence_score = 0.5
                
            return str(self.df)
            
        except Exception as e:
            # Try with different encoding or csv module if pandas fails
            try:
                with open(self.source_file, 'r', encoding='utf-8-sig') as file:
                    reader = csv.reader(file)
                    rows = list(reader)
                    
                if len(rows) > 0:
                    # Convert to DataFrame for consistent processing
                    self.df = pd.DataFrame(rows[1:], columns=rows[0])
                    self.confidence_score = 0.7
                    return str(self.df)
                else:
                    self.confidence_score = 0.3
                    return "Empty CSV file"
            except Exception as e2:
                self.confidence_score = 0.0
                return f"Error extracting content: {str(e)} / {str(e2)}"
    
    def extract_date_columns(self) -> Dict[str, List[str]]:
        """Extract dates from columns identified as date columns."""
        date_columns = {}
        
        if self.df is None or len(self.df) == 0:
            return date_columns
            
        # Look for columns that might contain dates
        for col in self.df.columns:
            col_lower = col.lower()
            if any(date_term in col_lower for date_term in self.date_columns):
                # This column likely contains dates
                dates = []
                for value in self.df[col].dropna():
                    try:
                        # Try to parse the date
                        if isinstance(value, str):
                            date_match = self.date_pattern.search(value)
                            if date_match:
                                normalized_date = self._normalize_date(date_match.group(1))
                                if normalized_date:
                                    dates.append(normalized_date)
                                    self.extracted_dates.add(normalized_date)
                        elif isinstance(value, datetime):
                            normalized_date = value.strftime("%Y-%m-%d")
                            dates.append(normalized_date)
                            self.extracted_dates.add(normalized_date)
                    except:
                        continue
                        
                if dates:
                    date_columns[col] = dates
                    
        return date_columns
    
    def extract_symptoms(self) -> Dict[str, Any]:
        """Extract symptom data if available."""
        symptoms = {}
        
        if self.df is None or len(self.df) == 0:
            return symptoms
            
        # Look for symptom columns
        symptom_col = None
        for col in self.df.columns:
            if col.lower() in self.symptom_columns:
                symptom_col = col
                break
                
        if not symptom_col:
            return symptoms
            
        # Find severity column if it exists
        severity_col = None
        for col in self.df.columns:
            if col.lower() in self.severity_columns:
                severity_col = col
                break
                
        # Find date column if it exists
        date_col = None
        for col in self.df.columns:
            if col.lower() in self.date_columns:
                date_col = col
                break
                
        # Extract symptom data
        for _, row in self.df.iterrows():
            symptom = row.get(symptom_col)
            if pd.isna(symptom) or not symptom:
                continue
                
            symptom_data = {"symptom": symptom}
            
            # Add severity if available
            if severity_col and not pd.isna(row.get(severity_col)):
                symptom_data["severity"] = row.get(severity_col)
                
            # Add date if available
            if date_col and not pd.isna(row.get(date_col)):
                date_value = row.get(date_col)
                if isinstance(date_value, str):
                    date_match = self.date_pattern.search(date_value)
                    if date_match:
                        normalized_date = self._normalize_date(date_match.group(1))
                        if normalized_date:
                            symptom_data["date"] = normalized_date
                            self.extracted_dates.add(normalized_date)
                elif isinstance(date_value, datetime):
                    symptom_data["date"] = date_value.strftime("%Y-%m-%d")
                    self.extracted_dates.add(date_value.strftime("%Y-%m-%d"))
                    
            # Add any other non-NA columns from this row
            for col in self.df.columns:
                if col not in [symptom_col, severity_col, date_col] and not pd.isna(row.get(col)):
                    symptom_data[col] = row.get(col)
                    
            # Use symptom as key, or append to list if symptom already exists
            if symptom in symptoms:
                if isinstance(symptoms[symptom], list):
                    symptoms[symptom].append(symptom_data)
                else:
                    symptoms[symptom] = [symptoms[symptom], symptom_data]
            else:
                symptoms[symptom] = symptom_data
                
        return symptoms
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize a date string to ISO format (YYYY-MM-DD)."""
        try:
            # Handle different separators
            if '/' in date_str:
                parts = date_str.split('/')
            elif '-' in date_str:
                parts = date_str.split('-')
            else:
                return None
                
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
                        
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return None
        except:
            return None
    
    def extract_dates(self) -> Set[str]:
        """Extract all dates from the CSV data."""
        if self.df is None or len(self.df) == 0:
            return set()
        
        # First check date columns
        self.extract_date_columns()
        
        # Also look for dates in any string columns
        for col in self.df.columns:
            if self.df[col].dtype == 'object':  # String columns
                for value in self.df[col].dropna():
                    if isinstance(value, str):
                        date_matches = self.date_pattern.findall(value)
                        for date_str in date_matches:
                            normalized_date = self._normalize_date(date_str)
                            if normalized_date:
                                self.extracted_dates.add(normalized_date)
        
        return self.extracted_dates
    
    def extract_sections(self) -> Dict[str, Any]:
        """Extract logical sections from the CSV data based on column groups."""
        sections = {}
        
        if self.df is None or len(self.df) == 0:
            return sections
        
        # Group by date if date column exists
        date_col = None
        for col in self.df.columns:
            if col.lower() in self.date_columns:
                date_col = col
                break
        
        if date_col:
            # Group data by date
            sections["by_date"] = {}
            for date, group in self.df.groupby(date_col):
                if isinstance(date, str):
                    date_match = self.date_pattern.search(date)
                    if date_match:
                        normalized_date = self._normalize_date(date_match.group(1))
                        if normalized_date:
                            sections["by_date"][normalized_date] = group.to_dict(orient='records')
                elif isinstance(date, datetime):
                    normalized_date = date.strftime("%Y-%m-%d")
                    sections["by_date"][normalized_date] = group.to_dict(orient='records')
        
        # Group by symptom/condition if such column exists
        symptom_col = None
        for col in self.df.columns:
            if col.lower() in self.symptom_columns:
                symptom_col = col
                break
        
        if symptom_col:
            # Group data by symptom/condition
            sections["by_symptom"] = {}
            for symptom, group in self.df.groupby(symptom_col):
                if pd.notna(symptom) and symptom:
                    sections["by_symptom"][symptom] = group.to_dict(orient='records')
        
        return sections
    
    def extract_providers(self) -> List[str]:
        """Extract healthcare provider names if present in the CSV data."""
        providers = []
        
        if self.df is None or len(self.df) == 0:
            return providers
        
        # Look for provider columns
        for col in self.df.columns:
            if col.lower() in self.provider_columns:
                # Extract unique provider names
                for provider in self.df[col].dropna().unique():
                    if isinstance(provider, str) and provider.strip():
                        providers.append(provider.strip())
        
        return providers

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Return the pandas dataframe representation of the CSV data."""
        return self.df
        
    def normalize_dates(self) -> bool:
        """Convert date columns to ISO format."""
        if self.df is None or not self.date_columns:
            return False
            
        try:
            for column in self.date_columns:
                self.df[column] = pd.to_datetime(
                    self.df[column], errors='coerce'
                ).dt.strftime('%Y-%m-%d')
            return True
        except:
            return False 