from pathlib import Path
from typing import Optional

from src.extraction.base import BaseExtractor
from src.extraction.csv_extractor import CSVExtractor
from src.extraction.markdown_extractor import MarkdownExtractor
from src.extraction.text_extractor import TextExtractor
from src.extraction.pdf_extractor import PDFExtractor
from src.extraction.html_extractor import HTMLExtractor
from src.extraction.rtf_extractor import RTFExtractor
from src.extraction.docx_extractor import DOCXExtractor


def get_extractor(file_path: Path) -> Optional[BaseExtractor]:
    """
    Factory function to get the appropriate extractor for a given file.
    
    Args:
        file_path: Path to the file to extract
        
    Returns:
        An instance of the appropriate extractor, or None if no suitable extractor is found
    """
    if not file_path.exists():
        return None
    
    file_extension = file_path.suffix.lower()
    
    # Map file extensions to extractors
    extractors = {
        '.txt': TextExtractor,
        '.md': MarkdownExtractor,
        '.csv': CSVExtractor,
        '.pdf': PDFExtractor,
        '.html': HTMLExtractor,
        '.htm': HTMLExtractor,
        '.rtf': RTFExtractor,
        '.docx': DOCXExtractor,
        '.doc': DOCXExtractor,  # Try to use DOCX extractor for legacy .doc files
    }
    
    # Get the extractor class based on file extension
    extractor_class = extractors.get(file_extension)
    
    # If no extractor found by extension, try to infer from content
    if not extractor_class:
        # Try to determine type by reading the first few bytes
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4096)
                content_type = infer_content_type(header, file_path.name)
                if content_type == 'text/csv':
                    extractor_class = CSVExtractor
                elif content_type == 'text/markdown':
                    extractor_class = MarkdownExtractor
                elif content_type == 'text/plain':
                    extractor_class = TextExtractor
                elif content_type == 'text/html':
                    extractor_class = HTMLExtractor
                elif content_type == 'application/pdf':
                    extractor_class = PDFExtractor
                elif content_type == 'application/rtf':
                    extractor_class = RTFExtractor
                elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    extractor_class = DOCXExtractor
        except Exception:
            # If we can't read the file or infer the type, default to text
            extractor_class = TextExtractor
    
    # Create and return the extractor instance if found
    if extractor_class:
        return extractor_class()
    
    return None


def infer_content_type(header: bytes, filename: str) -> str:
    """
    Attempt to infer the content type from the file header and name.
    
    Args:
        header: The first few bytes of the file
        filename: The name of the file
        
    Returns:
        A string representing the inferred content type
    """
    # Check for PDF signature
    if header.startswith(b'%PDF'):
        return 'application/pdf'
    
    # Check for RTF signature
    if header.startswith(b'{\\rtf'):
        return 'application/rtf'
    
    # Check for DOCX signature (it's a ZIP file with specific contents)
    if header.startswith(b'PK\x03\x04'):
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    # Check for HTML signature
    if header.startswith(b'<!DOCTYPE html') or header.startswith(b'<html') or b'<html' in header:
        return 'text/html'
    
    # Check if it's a text file
    try:
        header_text = header.decode('utf-8')
        
        # Check for HTML indicators
        if '<html' in header_text.lower() or '<body' in header_text.lower() or '<div' in header_text.lower():
            return 'text/html'
        
        # Check for CSV indicators
        if ',' in header_text and '\n' in header_text:
            line = header_text.split('\n')[0]
            # Check if first line has roughly equal number of commas
            if line.count(',') >= 2:
                return 'text/csv'
        
        # Check for Markdown indicators
        if '# ' in header_text or '## ' in header_text or '- ' in header_text:
            return 'text/markdown'
            
        # Default to plain text
        return 'text/plain'
    except UnicodeDecodeError:
        # If we can't decode as text, it's binary
        return 'application/octet-stream' 