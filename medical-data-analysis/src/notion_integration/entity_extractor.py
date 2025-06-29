"""
Entity Extractor

This module provides specialized extraction functions for different types of medical entities 
using a combination of LLM-based extraction and rule-based post-processing.
"""

import re
import json
import dateparser
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging
from pydantic import SecretStr

# Update imports for the latest LangChain version
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Define extraction prompts directly in this file since the import isn't working
# These would normally be imported from extraction_prompts.py

# Base prompt for medical document analysis
BASE_MEDICAL_DOCUMENT_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document content
and extract structured information as JSON.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all relevant medical entities from this document and format them as JSON.
Include appointments, medications, diagnoses, symptoms, and healthcare providers.
For each entity, include as much relevant information as possible, such as dates,
dosages, durations, severity, relationship to other entities, etc.

Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Appointment extraction prompt
APPOINTMENT_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all appointments mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all appointments mentioned in this document. Include past appointments,
current appointments being documented, and any scheduled future appointments.

For each appointment, extract:
- date (YYYY-MM-DD format if possible)
- time (if mentioned)
- doctor/provider name
- specialty
- location/facility
- purpose (if mentioned)
- notes or summary
- status (e.g., "Scheduled", "Completed", "Cancelled")

Format your response as a JSON array of appointment objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Medication extraction prompt
MEDICATION_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all medications mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all medications mentioned in this document. Include current medications,
discontinued medications, and newly prescribed medications.

For each medication, extract:
- name (use the most specific name mentioned)
- dosage (amount and unit, e.g., "10mg")
- frequency (e.g., "twice daily", "every 8 hours")
- start_date (YYYY-MM-DD format if mentioned)
- end_date (YYYY-MM-DD format if mentioned or if medication was discontinued)
- prescribing doctor (if mentioned)
- purpose/condition being treated (if mentioned)
- notes (any additional information)
- status (e.g., "Active", "Discontinued", "New prescription")

Format your response as a JSON array of medication objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Diagnosis extraction prompt
DIAGNOSIS_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all diagnoses/conditions mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all medical conditions, diagnoses, or disorders mentioned in this document.
Include confirmed diagnoses, suspected/possible diagnoses, and differential diagnoses.

For each diagnosis, extract:
- name (the specific condition name)
- status (e.g., "Confirmed", "Suspected", "Historical", "Ruled out")
- date (diagnosis date in YYYY-MM-DD format if mentioned)
- diagnosing doctor (if mentioned)
- symptoms related to this condition (if mentioned)
- treatments related to this condition (if mentioned)
- notes (any additional information)
- severity (if mentioned)

Format your response as a JSON array of diagnosis objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Symptom extraction prompt
SYMPTOM_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all symptoms mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all symptoms mentioned in this document, including chief complaints,
reported symptoms, and clinical observations.

For each symptom, extract:
- name (the specific symptom name)
- onset_date (when the symptom began, in YYYY-MM-DD format if mentioned)
- duration (how long the symptom has persisted, if mentioned)
- severity (e.g., "Mild", "Moderate", "Severe", or any scale mentioned)
- frequency (how often it occurs, if mentioned)
- location (body location, if applicable)
- related_condition (any associated diagnosis, if mentioned)
- notes (any additional information)
- status (e.g., "Current", "Resolved", "Improving", "Worsening")

Format your response as a JSON array of symptom objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Doctor extraction prompt
DOCTOR_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all healthcare providers/doctors mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all healthcare providers (doctors, specialists, nurses, etc.) mentioned in this document.

For each provider, extract:
- name (full name if available, or last name with title)
- specialty (area of medicine/expertise)
- facility/practice (hospital, clinic, or practice name if mentioned)
- contact information (phone, email, address if mentioned)
- role (e.g., "Primary Care Physician", "Specialist", "Consulting Physician")
- notes (any additional information)
- id (create a simple identifier based on name and specialty, e.g., "doc_smith_cardio")

Format your response as a JSON array of provider objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Configure logging
logger = logging.getLogger(__name__)


class EntityExtractor:
    """Handles extraction of medical entities from document text"""
    
    def __init__(self, 
                llm: Optional[ChatOpenAI] = None, 
                temperature: float = 0.1, 
                api_key: Optional[str] = None,
                model_name: str = "gpt-4o"):
        """
        Initialize the entity extractor
        
        Args:
            llm: Language model to use (if None, one will be created)
            temperature: Temperature for LLM sampling
            api_key: OpenAI API key (if not provided, uses environment variable)
            model_name: Name of the model to use
        """
        # Convert api_key to SecretStr if provided
        secret_api_key = SecretStr(api_key) if api_key else None
        
        self.llm = llm or ChatOpenAI(
            temperature=temperature,
            api_key=secret_api_key,
            model=model_name
        )
        
        # Create the base prompt template
        self.base_prompt = PromptTemplate.from_template(BASE_MEDICAL_DOCUMENT_PROMPT)
        
    def extract_entities(
        self, 
        text: str, 
        document_date: Optional[str] = None, 
        document_type: str = "Clinical Note"
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Extract medical entities from document text
        
        Args:
            text: Document text to extract entities from
            document_date: Date of the document (ISO format)
            document_type: Type of document (e.g., "Clinical Note", "Lab Report")
            
        Returns:
            Extracted entities as a dictionary or list of dictionaries
        """
        logger.info(f"Extracting entities from {document_type} dated {document_date}")
        
        # Create the extraction chain
        chain = (
            {"document_content": RunnablePassthrough(), 
             "document_date": lambda _: document_date or "", 
             "document_type": lambda _: document_type}
            | self.base_prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Run the chain
        try:
            response = chain.invoke(text)
            result = self._parse_llm_response(response)
            return result
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return None

    def _parse_llm_response(self, response: str) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Parse LLM JSON response safely
        
        Args:
            response: JSON string from LLM
            
        Returns:
            Parsed JSON data as dict or list
        """
        # Clean up the response to extract only JSON
        try:
            # Remove any markdown code block markers
            cleaned = re.sub(r'^```json\s*|\s*```$', '', response.strip())
            cleaned = re.sub(r'^```\s*|\s*```$', '', cleaned.strip())
            
            # Parse the JSON
            return json.loads(cleaned)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            logger.debug(f"Raw response: {response}")
            return None
        
    def normalize_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize date formats in the extracted data
        
        Args:
            data: Extracted data with possibly inconsistent date formats
            
        Returns:
            Data with normalized ISO 8601 date strings (YYYY-MM-DD)
        """
        if not data:
            return data
            
        def _normalize_date(date_str: str) -> str:
            if not date_str:
                return date_str
                
            try:
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    return parsed_date.strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(f"Could not parse date '{date_str}': {str(e)}")
                
            return date_str
            
        def _process_item(item: Any) -> Any:
            if isinstance(item, dict):
                return {k: _process_value(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [_process_value(v) for v in item]
            return item
                
        def _process_value(value: Any) -> Any:
            if isinstance(value, dict):
                return _process_item(value)
            elif isinstance(value, list):
                return [_process_item(v) for v in value]
            elif isinstance(value, str) and any(date_key in value.lower() for date_key in ["date", "when", "time"]):
                return _normalize_date(value)
            return value
            
        return _process_item(data)


def extract_entities_from_document(document_path: str, 
                                  extractor: EntityExtractor,
                                  document_date: Optional[str] = None,
                                  document_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract entities from a document file
    
    Args:
        document_path: Path to the document
        extractor: EntityExtractor instance
        document_date: Optional date of the document
        document_type: Optional type of the document
        
    Returns:
        Dictionary of extracted entities (possibly empty if extraction fails)
    """
    try:
        # Read document content
        with open(document_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Try to infer document date from filename if not provided
        if not document_date:
            date_match = re.search(r'(\d{4}[-_/]\d{1,2}[-_/]\d{1,2})', document_path)
            if date_match:
                document_date = date_match.group(1).replace('_', '-').replace('/', '-')
                
        # Try to infer document type from filename if not provided
        if not document_type:
            doc_types = {
                "lab": "Lab Results",
                "report": "Medical Report",
                "note": "Doctor's Note",
                "summary": "Visit Summary",
                "radiology": "Radiology Report",
                "consult": "Consultation",
                "letter": "Medical Letter"
            }
            
            for key, doc_type in doc_types.items():
                if key.lower() in document_path.lower():
                    document_type = doc_type
                    break
                    
            if not document_type:
                document_type = "Medical Document"
                
        # Extract entities
        entities = extractor.extract_entities(text, document_date, document_type)
        
        # Ensure we return a dictionary, even if extraction returns None or a list
        if entities is None:
            return {}
        elif isinstance(entities, list):
            # Convert list to dictionary with a default key
            return {"entities": entities}
        else:
            # Return the dictionary as is
            return entities
        
    except Exception as e:
        logger.error(f"Error extracting entities from document {document_path}: {str(e)}")
        return {} 