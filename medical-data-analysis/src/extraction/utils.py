"""
Utility functions for the extraction module.
"""

import os
from pathlib import Path
from typing import Union, List

# List of supported file extensions
SUPPORTED_EXTENSIONS = [
    '.txt', '.pdf', '.csv', '.html', '.htm', 
    '.md', '.rtf', '.docx', '.doc', '.xml'
]

def is_supported_file_type(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is of a supported type for extraction.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is of a supported type, False otherwise
    """
    file_path = Path(file_path)
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS

def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (lowercase, with dot)
    """
    file_path = Path(file_path)
    return file_path.suffix.lower()

def get_document_type_from_path(file_path: Union[str, Path]) -> str:
    """
    Attempt to determine document type from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Likely document type based on file path
    """
    file_path = str(file_path).lower()
    
    # Check for lab results
    if "lab" in file_path or "test" in file_path:
        return "lab_result"
    
    # Check for clinical notes
    if "note" in file_path or "clinical" in file_path or "doctor" in file_path:
        return "clinical_note"
    
    # Check for imaging results
    if "xray" in file_path or "x-ray" in file_path or "mri" in file_path or "ct" in file_path:
        return "imaging"
    
    # Check for patient history
    if "history" in file_path or "story" in file_path:
        return "patient_history"
    
    # Check for timeline
    if "timeline" in file_path:
        return "medical_timeline"
    
    # Check for symptoms
    if "symptom" in file_path:
        return "symptom_tracker"
    
    # Default to general medical document
    return "medical_document" 