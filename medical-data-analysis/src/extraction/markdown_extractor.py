import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

import pandas as pd

from src.extraction.base import BaseExtractor


class MarkdownExtractor(BaseExtractor):
    """Extractor for Markdown files including lab results and symptom reports."""
    
    def __init__(self):
        super().__init__()
        # Regular expressions for parsing markdown structures
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.*?)$', re.MULTILINE)
        self.table_pattern = re.compile(r'^\s*\|(.+)\|\s*$', re.MULTILINE)
        self.list_pattern = re.compile(r'^\s*[-*+]\s+(.*?)$', re.MULTILINE)
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b')
        
        # Lab test result patterns
        self.lab_result_pattern = re.compile(r'([a-zA-Z\s]+):\s*([<>]?\d+\.?\d*)\s*([a-zA-Z/%]+)?\s*(?:\(([^)]+)\))?')
        
        # Structure for parsed content
        self.headers = []
        self.tables = []
        self.lists = []
        self.sections = {}
        self.lab_results = []
        
        # For table detection and parsing
        self.table_divider_pattern = re.compile(r'^\|([-:\s]+)\|$', re.MULTILINE)
        
        self.extracted_dates = set()
    
    def _extract_metadata(self) -> Dict:
        """Extract metadata from the markdown file."""
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
        metadata["file_type"] = "markdown"
        metadata["file_name"] = self.source_file.name
        
        return metadata
    
    def _extract_content(self) -> str:
        """Extract content from the markdown file and handle different markdown structures."""
        try:
            with open(self.source_file, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Set confidence score based on content length and markdown features
            content_len = len(content)
            
            # Check for markdown-specific features
            has_headings = bool(self.header_pattern.search(content))
            has_list_items = bool(self.list_pattern.search(content))
            has_tables = bool(self.table_pattern.search(content) and self.table_divider_pattern.search(content))
            
            if content_len > 100 and (has_headings or has_list_items or has_tables):
                self.confidence_score = 1.0
            elif content_len > 50:
                self.confidence_score = 0.8
            else:
                self.confidence_score = 0.5
                
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(self.source_file, 'r', encoding='latin-1') as file:
                    content = file.read()
                self.confidence_score = 0.7  # Lower confidence due to encoding issues
                return content
            except Exception as e:
                self.confidence_score = 0.0
                return f"Error extracting content: {str(e)}"
        except Exception as e:
            self.confidence_score = 0.0
            return f"Error extracting content: {str(e)}"
    
    def _parse_headers(self, content: str) -> None:
        """Parse markdown headers."""
        self.headers = []
        matches = self.header_pattern.findall(content)
        for level, text in matches:
            self.headers.append({
                "level": len(level),  # Count number of # characters
                "text": text.strip()
            })
    
    def _parse_tables(self, content: str) -> None:
        """Parse markdown tables."""
        self.tables = []
        lines = content.split('\n')
        current_table = []
        in_table = False
        
        for line in lines:
            if '|' in line and line.strip():
                if not in_table:
                    in_table = True
                    current_table = [line]
                else:
                    current_table.append(line)
            elif in_table:
                # End of table
                in_table = False
                if len(current_table) > 1:  # At least header and separator
                    self.tables.append(self._process_table(current_table))
                current_table = []
                
        # Handle case where table is at end of file
        if in_table and len(current_table) > 1:
            self.tables.append(self._process_table(current_table))
    
    def _process_table(self, table_lines: List[str]) -> Dict:
        """Process a markdown table into a structured format."""
        if len(table_lines) < 2:
            return {"headers": [], "rows": []}
            
        # Process header row
        header_line = table_lines[0]
        headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
        
        # Skip separator row
        data_rows = []
        for i in range(2, len(table_lines)):
            row = table_lines[i]
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if len(cells) == len(headers):
                row_data = {headers[j]: cells[j] for j in range(len(headers))}
                data_rows.append(row_data)
                
        return {
            "headers": headers,
            "rows": data_rows
        }
    
    def _parse_lists(self, content: str) -> None:
        """Parse markdown lists."""
        self.lists = []
        matches = self.list_pattern.findall(content)
        for item in matches:
            self.lists.append(item.strip())
    
    def _extract_sections(self, content: str) -> None:
        """Extract content sections based on headers."""
        self.sections = {}
        if not self.headers:
            return
            
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            header_match = self.header_pattern.match(line)
            if header_match:
                # Save previous section
                if current_section:
                    self.sections[current_section] = '\n'.join(section_content)
                
                # Start new section
                current_section = header_match.group(2).strip()
                section_content = []
            elif current_section:
                section_content.append(line)
                
        # Save the last section
        if current_section:
            self.sections[current_section] = '\n'.join(section_content)
    
    def _extract_lab_results(self, content: str) -> None:
        """Extract lab test results from the content."""
        self.lab_results = []
        
        # First look in tables for structured lab results
        for table in self.tables:
            # Check if this is a lab results table by looking for common headers
            headers = [h.lower() for h in table["headers"]]
            if any(term in ' '.join(headers).lower() for term in 
                   ["test", "result", "value", "range", "reference", "lab"]):
                
                for row in table["rows"]:
                    lab_result = {
                        "test_name": None,
                        "value": None,
                        "unit": None,
                        "reference_range": None,
                        "abnormal": False,
                        "source": "table"
                    }
                    
                    # Map common column names to our fields
                    for header in row:
                        header_lower = header.lower()
                        if any(term in header_lower for term in ["test", "name", "component"]):
                            lab_result["test_name"] = row[header]
                        elif any(term in header_lower for term in ["result", "value"]):
                            value_str = row[header]
                            # Check for abnormal flags like H or L
                            if "H" in value_str or "high" in value_str.lower():
                                lab_result["abnormal"] = True
                            elif "L" in value_str or "low" in value_str.lower():
                                lab_result["abnormal"] = True
                                
                            # Extract numeric value
                            value_match = re.search(r'(\d+\.?\d*)', value_str)
                            if value_match:
                                lab_result["value"] = value_match.group(1)
                                
                            # Extract unit
                            unit_match = re.search(r'[^\d\s<>]+(g/dL|mg/dL|U/L|mmol/L|%|mg|g|mmHg|unit)', value_str)
                            if unit_match:
                                lab_result["unit"] = unit_match.group(1)
                        elif any(term in header_lower for term in ["range", "reference", "normal"]):
                            lab_result["reference_range"] = row[header]
                            
                    if lab_result["test_name"]:
                        self.lab_results.append(lab_result)
        
        # Next, look for lab results in the text content using regex
        for section_name, section_content in self.sections.items():
            # Check if this section is likely to contain lab results
            if any(term in section_name.lower() for term in 
                   ["lab", "test", "result", "blood", "urine", "panel"]):
                
                matches = self.lab_result_pattern.findall(section_content)
                for match in matches:
                    test_name, value, unit, reference = match
                    
                    # Only process if we have both a test name and value
                    if test_name.strip() and value.strip():
                        abnormal = ">" in value or "<" in value
                        value = re.sub(r'[<>]', '', value)  # Remove comparison symbols
                        
                        lab_result = {
                            "test_name": test_name.strip(),
                            "value": value.strip(),
                            "unit": unit.strip() if unit else None,
                            "reference_range": reference.strip() if reference else None,
                            "abnormal": abnormal,
                            "source": "text"
                        }
                        self.lab_results.append(lab_result)
    
    def extract_lab_test_date(self) -> Optional[str]:
        """Extract the date when lab tests were performed."""
        # First check the headers for dates
        for header in self.headers:
            date_matches = self.date_pattern.findall(header["text"])
            if date_matches:
                return self._normalize_date(date_matches[0])
        
        # Check the first few lines of content for dates
        first_lines = self.content.split('\n')[:10]
        for line in first_lines:
            date_matches = self.date_pattern.findall(line)
            if date_matches:
                return self._normalize_date(date_matches[0])
                
        # Use file date as fallback
        if "file_date" in self.metadata:
            return self.metadata["file_date"]
            
        return None
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize a date string to ISO 8601 format."""
        try:
            if '/' in date_str:
                parts = date_str.split('/')
            elif '-' in date_str:
                parts = date_str.split('-')
            else:
                return date_str
                
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
        except:
            pass
            
        return date_str
    
    def extract_headings(self) -> Dict[str, List[str]]:
        """Extract all headings from the markdown content, organized by level."""
        headings = {f"h{i}": [] for i in range(1, 7)}
        
        if not self.content:
            return headings
            
        matches = self.header_pattern.findall(self.content)
        for match in matches:
            level = len(match[0])  # Number of # characters
            heading_text = match[1].strip()
            headings[f"h{level}"].append(heading_text)
            
        return headings
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """Extract tables from the markdown content."""
        tables = []
        
        if not self.content:
            return tables
            
        # Split content by lines
        lines = self.content.split('\n')
        
        i = 0
        while i < len(lines):
            if self.table_pattern.match(lines[i]):
                # Check if the next line is a table divider
                if i + 1 < len(lines) and self.table_divider_pattern.match(lines[i + 1]):
                    # Found the start of a table
                    table_lines = []
                    table_lines.append(lines[i])
                    table_lines.append(lines[i + 1])
                    i += 2
                    
                    # Collect the rest of the table rows
                    while i < len(lines) and self.table_pattern.match(lines[i]):
                        table_lines.append(lines[i])
                        i += 1
                    
                    # Parse the table
                    if len(table_lines) > 2:  # Header, divider, and at least one row
                        table = self._parse_markdown_table(table_lines)
                        if not table.empty:
                            tables.append(table)
                    continue
            i += 1
            
        return tables
    
    def _parse_markdown_table(self, table_lines: List[str]) -> pd.DataFrame:
        """Parse a markdown table into a pandas DataFrame."""
        # Extract headers
        headers = table_lines[0].strip('|').split('|')
        headers = [h.strip() for h in headers]
        
        # Extract data rows
        data = []
        for line in table_lines[2:]:  # Skip header and divider
            row_data = line.strip('|').split('|')
            row_data = [cell.strip() for cell in row_data]
            data.append(row_data)
        
        # Create DataFrame
        try:
            df = pd.DataFrame(data, columns=headers)
            return df
        except Exception:
            return pd.DataFrame()
    
    def extract_lab_results(self) -> Dict[str, Dict[str, str]]:
        """Extract lab results from markdown tables."""
        lab_results = {}
        
        tables = self.extract_tables()
        for table in tables:
            # Check if this looks like a lab results table
            if len(table.columns) >= 2:
                test_col = None
                result_col = None
                range_col = None
                
                # Try to identify columns
                for col in table.columns:
                    col_lower = col.lower()
                    if 'test' in col_lower or 'lab' in col_lower or 'exam' in col_lower:
                        test_col = col
                    elif 'result' in col_lower or 'value' in col_lower:
                        result_col = col
                    elif 'range' in col_lower or 'normal' in col_lower or 'reference' in col_lower:
                        range_col = col
                
                # If we found a test column and result column
                if test_col and result_col:
                    for _, row in table.iterrows():
                        test_name = row[test_col]
                        result = row[result_col]
                        
                        # Add normal range if available
                        result_data = {"value": result}
                        if range_col and pd.notna(row.get(range_col)):
                            result_data["normal_range"] = row[range_col]
                            
                        lab_results[test_name] = result_data
        
        return lab_results
    
    def extract_dates(self) -> Set[str]:
        """Extract all dates mentioned in the markdown content."""
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
        """Extract sections from the markdown content based on headings."""
        sections = {}
        
        if not self.content:
            return sections
            
        # Split content by lines
        lines = self.content.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            heading_match = self.header_pattern.match(line)
            if heading_match:
                # Save previous section
                if current_section:
                    sections[current_section.lower()] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = heading_match.group(2).strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save the last section
        if current_section:
            sections[current_section.lower()] = '\n'.join(current_content).strip()
            
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