from typing import Dict, Optional, Any

from src.processing.base import BaseProcessor
from src.processing.medical_text_processor import MedicalTextProcessor
from src.processing.lab_results_processor import LabResultsProcessor


class ProcessorFactory:
    """Factory class for creating and managing processors."""
    
    @staticmethod
    def get_processor(document_type: str) -> BaseProcessor:
        """
        Get the appropriate processor for a given document type.
        
        Args:
            document_type: Type of document (lab_result, medical_note, etc.)
            
        Returns:
            An instance of the appropriate processor
        """
        processors = {
            "lab_result": LabResultsProcessor(),
            "lab_report": LabResultsProcessor(),
            "medical_note": MedicalTextProcessor(),
            "clinical_note": MedicalTextProcessor(),
            "doctor_letter": MedicalTextProcessor(),
            "medical_history": MedicalTextProcessor(),
            "discharge_summary": MedicalTextProcessor(),
            "consultation": MedicalTextProcessor(),
            "assessment": MedicalTextProcessor(),
            "referral": MedicalTextProcessor(),
            "imaging_report": MedicalTextProcessor(),
            "test_result": LabResultsProcessor(),
            "patient_narrative": MedicalTextProcessor(),
        }
        
        # Make sure document_type is a string before calling lower()
        if isinstance(document_type, str):
            lookup_key = document_type.lower()
        else:
            # Handle case where document_type might be a dict or other type
            lookup_key = str(document_type).lower()
        
        # Default to MedicalTextProcessor if no specific processor is found
        return processors.get(lookup_key, MedicalTextProcessor())
    
    @staticmethod
    def determine_document_type(extracted_data: Dict[str, Any]) -> str:
        """
        Determine the document type from extracted data.
        
        Args:
            extracted_data: Dictionary containing extracted document data
            
        Returns:
            String representing the document type
        """
        # If the extractor already determined the document type, use that
        if "document_type" in extracted_data:
            return extracted_data["document_type"]
        
        # Get file path from metadata
        file_path = extracted_data.get("metadata", {}).get("file_path", "")
        file_name = extracted_data.get("metadata", {}).get("file_name", "")
        
        # Look for keywords in the content or file name
        content = extracted_data.get("content", "").lower()
        
        # Try to determine document type from content keywords
        document_type_keywords = {
            "lab_result": ["lab result", "laboratory", "test result", "blood test", "panel", "specimen"],
            "medical_note": ["progress note", "clinical note", "medical note", "soap note"],
            "assessment": ["assessment", "examination", "physical exam"],
            "discharge_summary": ["discharge summary", "discharged from"],
            "consultation": ["consultation", "consult", "referred for"],
            "imaging_report": ["mri", "ct scan", "x-ray", "ultrasound", "imaging", "radiology"],
            "referral": ["referral", "referring physician"],
            "patient_narrative": ["personal history", "my symptoms", "symptom journal", "diary"]
        }
        
        for doc_type, keywords in document_type_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    return doc_type
        
        # Check if this looks like lab results based on the structure
        if "lab_results" in extracted_data and extracted_data["lab_results"]:
            return "lab_result"
        
        # Check file name/path for clues
        file_name_lower = file_name.lower()
        if "lab" in file_name_lower or "test" in file_name_lower:
            return "lab_result"
        elif "note" in file_name_lower or "letter" in file_name_lower:
            return "medical_note"
        elif "report" in file_name_lower:
            return "medical_note"
        elif "consult" in file_name_lower:
            return "consultation"
        elif "narrative" in file_name_lower or "journal" in file_name_lower:
            return "patient_narrative"
        
        # Default to medical_note if we can't determine the type
        return "medical_note"
    
    @staticmethod
    def process_document(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document using the appropriate processor.
        
        Args:
            extracted_data: Dictionary containing extracted document data
            
        Returns:
            Dictionary with processed document data
        """
        # Determine document type
        document_type = ProcessorFactory.determine_document_type(extracted_data)
        
        # Add determined document type to metadata
        if "metadata" not in extracted_data:
            extracted_data["metadata"] = {}
        extracted_data["metadata"]["document_type"] = document_type
        
        # Get appropriate processor
        processor = ProcessorFactory.get_processor(document_type)
        
        # Process the data
        processed_data = processor.process(extracted_data)
        
        return processed_data


def get_processor(document_type: str) -> Optional[BaseProcessor]:
    """
    Factory function to get the appropriate processor for a given document type.
    
    Args:
        document_type: Type of document (lab_result, medical_note, etc.)
        
    Returns:
        An instance of the appropriate processor, or None if no suitable processor is found
    """
    return ProcessorFactory.get_processor(document_type)


def determine_document_type(extracted_data: Dict[str, Any]) -> str:
    """
    Determine the document type from extracted data.
    
    Args:
        extracted_data: Dictionary containing extracted document data
        
    Returns:
        String representing the document type
    """
    return ProcessorFactory.determine_document_type(extracted_data)


def process_document(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a document using the appropriate processor.
    
    Args:
        extracted_data: Dictionary containing extracted document data
        
    Returns:
        Dictionary with processed document data
    """
    return ProcessorFactory.process_document(extracted_data) 