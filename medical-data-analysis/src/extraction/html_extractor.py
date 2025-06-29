import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from bs4 import BeautifulSoup
import html2text

from src.extraction.base import BaseExtractor


class HTMLExtractor(BaseExtractor):
    """Extractor for HTML files (medical portals, exported medical records, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.soup = None
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b')
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.ignore_tables = False
        self.html_converter.body_width = 0  # No wrapping
        
        # Common medical sections in HTML exports
        self.medical_sections = [
            "patient information", "medications", "allergies", "medical history",
            "vital signs", "lab results", "diagnoses", "procedures", "immunizations",
            "family history", "social history", "assessment", "plan", "treatment"
        ]
    
    def _extract_metadata(self) -> Dict:
        """Extract metadata from the HTML file."""
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
        metadata["file_type"] = "html"
        metadata["file_name"] = self.source_file.name
        
        # Parse HTML with BeautifulSoup for metadata
        try:
            with open(self.source_file, 'r', encoding='utf-8') as file:
                self.soup = BeautifulSoup(file, 'html.parser')
                
                # Extract title if available
                title_tag = self.soup.find('title')
                if title_tag and title_tag.string:
                    metadata["html_title"] = title_tag.string.strip()
                
                # Extract meta tags
                meta_tags = self.soup.find_all('meta')
                for meta in meta_tags:
                    name = meta.get('name')
                    content = meta.get('content')
                    if name and content:
                        metadata[f"meta_{name}"] = content
                
                # Look for dates in the HTML content
                dates = self.extract_dates_from_soup()
                if dates:
                    metadata["extracted_dates"] = list(dates)[:5]  # Limit to first 5 dates
                
                # Look for medical provider information
                providers = self.extract_medical_providers_from_soup()
                if providers:
                    metadata["medical_providers"] = providers[:3]  # Limit to first 3 providers
        except Exception as e:
            metadata["html_metadata_error"] = str(e)
        
        return metadata
    
    def _extract_content(self) -> str:
        """Extract content from the HTML file."""
        try:
            # Try with UTF-8 encoding first
            with open(self.source_file, 'r', encoding='utf-8') as file:
                html_content = file.read()
                
                # Parse with BeautifulSoup for structured extraction
                if not self.soup:
                    self.soup = BeautifulSoup(html_content, 'html.parser')
                
                # Convert HTML to markdown for better text representation
                markdown_content = self.html_converter.handle(html_content)
                
                # Set confidence score based on content extraction
                if markdown_content and len(markdown_content) > 100:
                    self.confidence_score = 1.0
                elif markdown_content:
                    self.confidence_score = 0.8
                else:
                    self.confidence_score = 0.3
                    
                return markdown_content
                
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(self.source_file, 'r', encoding='latin-1') as file:
                    html_content = file.read()
                    
                    # Parse with BeautifulSoup for structured extraction
                    self.soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Convert HTML to markdown
                    markdown_content = self.html_converter.handle(html_content)
                    
                    self.confidence_score = 0.7  # Lower confidence due to encoding issues
                    return markdown_content
            except Exception as e:
                self.confidence_score = 0.0
                return f"Error extracting content: {str(e)}"
        except Exception as e:
            self.confidence_score = 0.0
            return f"Error extracting content: {str(e)}"
    
    def extract_dates_from_soup(self) -> Set[str]:
        """Extract dates from HTML content using BeautifulSoup."""
        dates = set()
        
        if not self.soup:
            return dates
        
        # Look for dates in text content
        text_content = self.soup.get_text()
        date_matches = self.date_pattern.findall(text_content)
        
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
                    dates.add(normalized_date)
            except:
                continue
                
        return dates
    
    def extract_tables(self) -> List[Dict]:
        """Extract tables from HTML content."""
        tables = []
        
        if not self.soup:
            return tables
        
        table_elements = self.soup.find_all('table')
        
        for i, table in enumerate(table_elements):
            table_data = {
                "id": i,
                "headers": [],
                "rows": []
            }
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
                table_data["headers"] = headers
                
                # Extract rows
                data_rows = table.find_all('tr')[1:] if headers else table.find_all('tr')
                for row in data_rows:
                    cells = [td.get_text().strip() for td in row.find_all('td')]
                    if cells and len(cells) == len(headers):
                        row_dict = {headers[j]: cells[j] for j in range(len(headers))}
                        table_data["rows"].append(row_dict)
                    elif cells:
                        table_data["rows"].append(cells)
            
            # Only add tables with actual data
            if table_data["rows"]:
                tables.append(table_data)
        
        return tables
    
    def extract_medical_providers_from_soup(self) -> List[str]:
        """Extract potential healthcare provider names or organizations."""
        providers = set()
        
        if not self.soup:
            return list(providers)
        
        # Common patterns for medical providers in HTML
        provider_patterns = [
            re.compile(r'Dr\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', re.IGNORECASE),
            re.compile(r'Doctor\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', re.IGNORECASE),
            re.compile(r'([A-Z][a-z]+\s+Clinic)', re.IGNORECASE),
            re.compile(r'([A-Z][a-z]+\s+Hospital)', re.IGNORECASE),
            re.compile(r'Department\s+of\s+([A-Z][a-z]+)', re.IGNORECASE)
        ]
        
        text_content = self.soup.get_text()
        
        for pattern in provider_patterns:
            matches = pattern.findall(text_content)
            for match in matches:
                providers.add(match.strip())
        
        return list(providers)
    
    def extract_sections(self) -> Dict[str, str]:
        """Extract structured sections from the HTML content."""
        sections = {}
        
        if not self.soup:
            return sections
        
        # Try to find common medical sections
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            heading_text = heading.get_text().strip().lower()
            
            # Check if this heading matches a medical section
            for section_name in self.medical_sections:
                if section_name in heading_text:
                    # Extract content until next heading
                    content = []
                    current = heading.next_sibling
                    
                    while current and not current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if hasattr(current, 'get_text'):
                            text = current.get_text().strip()
                            if text:
                                content.append(text)
                        current = current.next_sibling
                    
                    if content:
                        sections[heading_text] = '\n'.join(content)
        
        # If we didn't find structured sections, try using div elements with class or id
        if not sections:
            for section_name in self.medical_sections:
                # Look for divs with class or id containing section name
                divs = self.soup.find_all('div', class_=lambda c: c and section_name in c.lower())
                divs.extend(self.soup.find_all('div', id=lambda i: i and section_name in i.lower()))
                
                for div in divs:
                    sections[section_name] = div.get_text().strip()
        
        return sections

    def clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content by removing non-essential elements.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned text content
        """
        # You might want to use BeautifulSoup or other libraries for better HTML parsing
        # This is a simple approach to get text content
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "meta", "link", "noscript"]):
                script.extract()
            
            # Get text and normalize whitespace
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
        except ImportError:
            # Fallback to basic regex cleaning if BeautifulSoup is not available
            import re
            text = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<.*?>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
    
    def extract(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract content and metadata from an HTML file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        return self.process_file(file_path) 