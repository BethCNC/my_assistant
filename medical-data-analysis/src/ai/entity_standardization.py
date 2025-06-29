"""
Medical Entity Standardization

This module provides functions for standardizing medical entities
to canonical forms and mapping them to standard terminologies.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

# Sample mappings for standardization - would be more extensive in production
CONDITION_MAPPINGS = {
    "diabetes": "Diabetes Mellitus",
    "diabetes mellitus": "Diabetes Mellitus",
    "dm": "Diabetes Mellitus",
    "t1d": "Type 1 Diabetes Mellitus",
    "t2d": "Type 2 Diabetes Mellitus",
    "hypertension": "Hypertension",
    "htn": "Hypertension",
    "high blood pressure": "Hypertension",
    "asthma": "Asthma",
    "gerd": "Gastroesophageal Reflux Disease",
    "acid reflux": "Gastroesophageal Reflux Disease",
    "migraine": "Migraine",
    "migraine headache": "Migraine",
    "eds": "Ehlers-Danlos Syndrome",
    "ehlers danlos": "Ehlers-Danlos Syndrome",
    "heds": "Hypermobile Ehlers-Danlos Syndrome",
    "hypermobile eds": "Hypermobile Ehlers-Danlos Syndrome",
    "asd": "Autism Spectrum Disorder",
    "autism": "Autism Spectrum Disorder",
    "adhd": "Attention Deficit Hyperactivity Disorder",
    "add": "Attention Deficit Hyperactivity Disorder",
    "pots": "Postural Orthostatic Tachycardia Syndrome",
    "postural orthostatic tachycardia syndrome": "Postural Orthostatic Tachycardia Syndrome"
}

MEDICATION_MAPPINGS = {
    "tylenol": "Acetaminophen",
    "acetaminophen": "Acetaminophen",
    "ibuprofen": "Ibuprofen",
    "advil": "Ibuprofen",
    "motrin": "Ibuprofen",
    "aspirin": "Aspirin",
    "lisinopril": "Lisinopril",
    "metformin": "Metformin",
    "lipitor": "Atorvastatin",
    "atorvastatin": "Atorvastatin",
}

def standardize_medical_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize a medical entity by mapping terminology to canonical forms.
    
    Args:
        entity: The medical entity dictionary
        
    Returns:
        Standardized entity dictionary
    """
    entity_type = entity.get("type", "").lower()
    
    # Create a copy to avoid modifying the original
    standardized = entity.copy()
    
    # Get entity name/text from either field
    entity_text = standardized.get("text", standardized.get("name", "")).lower()
    
    # Add standard name field expected by tests
    if "standard_name" not in standardized:
        if entity_type == "condition" or entity_type == "diagnosis":
            standardized["standard_name"] = CONDITION_MAPPINGS.get(entity_text, standardized.get("text", standardized.get("name", "")))
            
            # Add ICD-10 code if missing
            if "icd10" not in standardized:
                standardized["icd10"] = get_icd10_code(entity_text)
                
        elif entity_type == "medication" or entity_type == "drug":
            standardized["standard_name"] = MEDICATION_MAPPINGS.get(entity_text, standardized.get("text", standardized.get("name", "")))
            
            # Try to standardize dosage format
            if "dosage" in standardized:
                standardized["dosage"] = standardize_dosage(standardized["dosage"])
                
        elif entity_type == "symptom":
            # Keep original for symptoms that don't have standard mappings
            standardized["standard_name"] = standardized.get("text", standardized.get("name", ""))
            
        elif entity_type == "treatment":
            # Keep original for treatments that don't have standard mappings
            standardized["standard_name"] = standardized.get("text", standardized.get("name", ""))
                
        elif entity_type == "lab_result":
            # Standardize lab result names and units
            if "test_name" in standardized:
                standardized["test_name"] = standardize_lab_name(standardized["test_name"])
            if "unit" in standardized:
                standardized["unit"] = standardize_unit(standardized["unit"])
    
    # Add confidence score for standardization
    if "standardization_confidence" not in standardized:
        if entity_text == standardized.get("standard_name", "").lower():
            standardized["standardization_confidence"] = 0.5  # Same name, not found in mappings
        else:
            standardized["standardization_confidence"] = 0.9  # Found in mappings
    
    return standardized

def standardize_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Standardize a list of medical entities.
    
    Args:
        entities: List of entity dictionaries
        
    Returns:
        List of standardized entity dictionaries
    """
    return [standardize_medical_entity(entity) for entity in entities]

def get_icd10_code(condition_name: str) -> Optional[str]:
    """
    Get ICD-10 code for a condition name.
    
    This is a simplified implementation. In production, this would
    connect to a comprehensive medical terminology database.
    
    Args:
        condition_name: Name of the medical condition
        
    Returns:
        ICD-10 code or None if not found
    """
    # Example mapping - would be more extensive in production
    icd10_mapping = {
        "diabetes mellitus": "E11.9",
        "type 1 diabetes mellitus": "E10.9",
        "type 2 diabetes mellitus": "E11.9", 
        "hypertension": "I10",
        "asthma": "J45.909",
        "migraine": "G43.909",
        "gastroesophageal reflux disease": "K21.9",
        "ehlers-danlos syndrome": "Q79.6",
        "hypermobile ehlers-danlos syndrome": "Q79.6",
        "autism spectrum disorder": "F84.0",
        "attention deficit hyperactivity disorder": "F90.9",
        "postural orthostatic tachycardia syndrome": "I49.8",
        "pots": "I49.8",
    }
    
    return icd10_mapping.get(condition_name.lower())

def standardize_dosage(dosage: str) -> str:
    """
    Standardize medication dosage format.
    
    Args:
        dosage: Original dosage string
        
    Returns:
        Standardized dosage string
    """
    # Remove extra spaces
    dosage = re.sub(r'\s+', ' ', dosage.strip())
    
    # Standardize common abbreviations
    dosage = re.sub(r'\bmg\b', 'mg', dosage, flags=re.IGNORECASE)
    dosage = re.sub(r'\bml\b', 'mL', dosage, flags=re.IGNORECASE)
    dosage = re.sub(r'\bmcg\b', 'μg', dosage, flags=re.IGNORECASE)
    
    # Standardize frequency notation
    dosage = re.sub(r'\bq(\d+)h\b', r'every \1 hours', dosage, flags=re.IGNORECASE)
    dosage = re.sub(r'\bqd\b', 'daily', dosage, flags=re.IGNORECASE)
    dosage = re.sub(r'\bbid\b', 'twice daily', dosage, flags=re.IGNORECASE)
    dosage = re.sub(r'\btid\b', 'three times daily', dosage, flags=re.IGNORECASE)
    dosage = re.sub(r'\bqid\b', 'four times daily', dosage, flags=re.IGNORECASE)
    
    return dosage

def standardize_lab_name(lab_name: str) -> str:
    """
    Standardize laboratory test names.
    
    Args:
        lab_name: Original lab test name
        
    Returns:
        Standardized lab test name
    """
    # Example mapping - would be more extensive in production
    lab_mapping = {
        "a1c": "Hemoglobin A1c",
        "hba1c": "Hemoglobin A1c",
        "cbc": "Complete Blood Count",
        "bmp": "Basic Metabolic Panel",
        "cmp": "Comprehensive Metabolic Panel",
        "lipid panel": "Lipid Panel",
        "tsh": "Thyroid Stimulating Hormone",
    }
    
    return lab_mapping.get(lab_name.lower(), lab_name)

def standardize_unit(unit: str) -> str:
    """
    Standardize measurement units.
    
    Args:
        unit: Original unit string
        
    Returns:
        Standardized unit string
    """
    # Example mapping - would be more extensive in production
    unit_mapping = {
        "milligrams": "mg",
        "mg": "mg",
        "milliliters": "mL",
        "ml": "mL",
        "micrograms": "μg",
        "mcg": "μg",
        "millimoles per liter": "mmol/L",
        "mm/l": "mmol/L",
        "mmol/l": "mmol/L",
        "milligrams per deciliter": "mg/dL",
        "mg/dl": "mg/dL",
    }
    
    return unit_mapping.get(unit.lower(), unit) 