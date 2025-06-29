"""
Medical Text Analysis

This module provides functionality for analyzing medical text and extracting insights.
"""
import logging
import json
import re
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalTextAnalyzer:
    """Analyzes medical text to extract semantic meaning and relationships."""
    
    def __init__(self, model_name: str = "default-medical-nlp"):
        """Initialize the medical text analyzer.
        
        Args:
            model_name: Name of the model to use for text analysis
        """
        self.model_name = model_name
        logger.info(f"Initializing Medical Text Analyzer with model {model_name}")
        
        # Define medical specialties and related terms
        self.specialties = {
            "GP": ["general practitioner", "family medicine", "primary care", "physician", "family doctor", "gp visit"],
            "Cardiology": ["cardiology", "cardiologist", "heart", "cardiac", "cardiovascular"],
            "Neurology": ["neurology", "neurologist", "nerve", "brain", "neurological", "migraine", "seizure"],
            "Endocrinology": ["endocrinology", "endocrinologist", "hormone", "thyroid", "diabetes", "endocrine"],
            "Rheumatology": ["rheumatology", "rheumatologist", "arthritis", "joint", "autoimmune", "lupus", "fibromyalgia"],
            "Gastroenterology": ["gastroenterology", "gastroenterologist", "digestive", "stomach", "gi", "bowel", "colon"],
            "Dermatology": ["dermatology", "dermatologist", "skin", "rash", "mole", "acne"],
            "Orthopedics": ["orthopedic", "orthopedist", "bone", "joint", "fracture", "sports medicine", "orthopedics"],
            "Gynecology": ["gynecology", "gynecologist", "obgyn", "ob/gyn", "women's health", "pap smear"],
            "Urology": ["urology", "urologist", "urinary", "bladder", "kidney", "prostate"],
            "ENT": ["ent", "ear, nose, and throat", "otolaryngology", "otolaryngologist", "sinus", "hearing"],
            "Ophthalmology": ["ophthalmology", "ophthalmologist", "eye", "vision", "retina", "optometry"],
            "Psychiatry": ["psychiatry", "psychiatrist", "mental health", "depression", "anxiety", "bipolar"],
            "Psychology": ["psychology", "psychologist", "therapy", "counseling", "mental health", "behavioral"],
            "Physical Therapy": ["physical therapy", "physiotherapy", "rehabilitation", "pt", "exercise therapy"],
            "Genetics": ["genetic", "genetics", "geneticist", "dna", "chromosome", "hereditary"],
            "Pulmonology": ["pulmonology", "pulmonologist", "lung", "respiratory", "breathing", "asthma"],
            "Immunology": ["immunology", "immunologist", "immune", "allergy", "allergist", "autoimmune"],
            "Nephrology": ["nephrology", "nephrologist", "kidney", "renal", "dialysis"],
            "Hematology": ["hematology", "hematologist", "blood", "anemia", "leukemia"],
            "Oncology": ["oncology", "oncologist", "cancer", "tumor", "chemotherapy", "radiation"]
        }
        
        # Define lab test types and related terms
        self.lab_tests = {
            "Complete Blood Count": ["cbc", "complete blood count", "blood count", "hemoglobin", "wbc", "rbc", "platelets"],
            "Comprehensive Metabolic Panel": ["cmp", "comprehensive metabolic panel", "metabolic panel", "electrolytes", "kidney function", "liver function"],
            "Lipid Panel": ["lipid", "cholesterol", "hdl", "ldl", "triglycerides", "lipid panel"],
            "Thyroid Function Tests": ["thyroid", "tsh", "t3", "t4", "thyroid stimulating hormone"],
            "Urinalysis": ["urinalysis", "urine test", "urine sample", "urine analysis"],
            "HbA1c": ["hba1c", "a1c", "glycated hemoglobin", "diabetes test"],
            "Vitamin D": ["vitamin d", "25-hydroxy", "vitamin d level"],
            "Iron Panel": ["iron", "ferritin", "transferrin", "iron panel", "iron levels"],
            "Coagulation Panel": ["coagulation", "clotting", "pt", "inr", "ptt", "prothrombin"],
            "Liver Function Tests": ["liver function", "liver enzymes", "alt", "ast", "alp", "bilirubin"],
            "Kidney Function Tests": ["kidney function", "renal function", "bun", "creatinine", "egfr"],
            "Blood Glucose": ["glucose", "blood sugar", "fasting glucose", "glucose test"]
        }
        
        # Define procedure types and related terms
        self.procedures = {
            "X-ray": ["x-ray", "xray", "radiograph", "chest x-ray", "bone x-ray"],
            "MRI": ["mri", "magnetic resonance imaging", "brain mri", "spine mri", "joint mri"],
            "CT Scan": ["ct", "cat scan", "computed tomography", "ct scan"],
            "Ultrasound": ["ultrasound", "sonogram", "ultrasonography", "doppler"],
            "Colonoscopy": ["colonoscopy", "colon examination", "colon screening"],
            "Endoscopy": ["endoscopy", "upper gi", "upper endoscopy", "egd"],
            "Biopsy": ["biopsy", "tissue sample", "needle biopsy", "surgical biopsy"],
            "EKG/ECG": ["ekg", "ecg", "electrocardiogram", "cardiac monitoring"],
            "Stress Test": ["stress test", "exercise test", "treadmill test", "cardiac stress"],
            "PET Scan": ["pet", "positron emission tomography", "pet scan", "pet-ct"],
            "Mammogram": ["mammogram", "mammography", "breast examination", "breast screening"],
            "Electromyography": ["emg", "electromyography", "nerve conduction", "muscle testing"],
            "Echocardiogram": ["echocardiogram", "echo", "cardiac ultrasound", "heart ultrasound"]
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze medical text to extract meaning and relationships.
        
        Args:
            text: Medical text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Analyzing medical text")
        
        # Simple analysis implementation
        result = {
            "sentiment": "neutral",
            "entities": self._extract_entities(text),
            "key_terms": self._extract_key_terms(text),
            "temporal_references": self._extract_temporal_references(text)
        }
        
        return result
    
    def identify_appointment_type(self, text: str) -> str:
        """Identify the type of medical appointment from text description.
        
        Args:
            text: Text description of the appointment
            
        Returns:
            Appointment type (e.g., "Cardiology", "Neurology")
        """
        logger.debug(f"Identifying appointment type from: {text[:100]}...")
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # Check for each specialty
        for specialty, keywords in self.specialties.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                if specialty == "GP":
                    return f"GP appointment"
                return f"{specialty} appointment"
        
        # If no specific specialty is found
        return "Medical appointment"  # Generic medical appointment
    
    def identify_lab_test_type(self, text: str) -> str:
        """Identify the type of lab test from text description.
        
        Args:
            text: Text description of the lab test
            
        Returns:
            Lab test type (e.g., "Complete Blood Count", "Lipid Panel")
        """
        logger.debug(f"Identifying lab test type from: {text[:100]}...")
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # Return generic lab results name as requested by user
        return "Lab results"
    
    def identify_procedure_type(self, text: str) -> str:
        """Identify the type of medical procedure from text description.
        
        Args:
            text: Text description of the procedure
            
        Returns:
            Procedure type (e.g., "MRI", "X-ray", "Colonoscopy")
        """
        logger.debug(f"Identifying procedure type from: {text[:100]}...")
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # Check for each procedure type
        for procedure_type, keywords in self.procedures.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                if procedure_type in ["MRI", "X-ray", "CT Scan"]:
                    return f"{procedure_type}"
                return f"{procedure_type} procedure"
        
        # If no specific procedure type is found
        return "Medical procedure"
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical entities from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted entities with their types
        """
        entities = []
        
        # This is a simple implementation - in production, this would use a proper NER model
        # Look for patterns like medication dosages
        medication_pattern = r'(\b[A-Z][a-z]+(?:in|ol|ide|ine|one|ate|ium|en)\b)\s+(\d+(?:\.\d+)?)\s?(mg|g|mcg|mL)'
        for match in re.finditer(medication_pattern, text):
            entities.append({
                "text": match.group(0),
                "type": "MEDICATION",
                "start": match.start(),
                "end": match.end()
            })
        
        return entities
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key medical terms from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of key medical terms
        """
        # Simple key term extraction 
        key_terms = []
        
        # Check for specialty terms
        for specialty, terms in self.specialties.items():
            for term in terms:
                if term.lower() in text.lower():
                    key_terms.append(specialty)
                    break
        
        # Check for lab test terms
        for test, terms in self.lab_tests.items():
            for term in terms:
                if term.lower() in text.lower():
                    key_terms.append(test)
                    break
        
        # Check for procedure terms
        for procedure, terms in self.procedures.items():
            for term in terms:
                if term.lower() in text.lower():
                    key_terms.append(procedure)
                    break
        
        return list(set(key_terms))  # Remove duplicates
    
    def _extract_temporal_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract temporal references from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted temporal references
        """
        references = []
        
        # Look for date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY or DD-MM-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                references.append({
                    "text": match.group(0),
                    "type": "DATE",
                    "start": match.start(),
                    "end": match.end()
                })
        
        # Look for time references
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s?(?:am|pm|AM|PM)\b',  # HH:MM am/pm
            r'\b\d{1,2}\s?(?:am|pm|AM|PM)\b'  # HH am/pm
        ]
        
        for pattern in time_patterns:
            for match in re.finditer(pattern, text):
                references.append({
                    "text": match.group(0),
                    "type": "TIME",
                    "start": match.start(),
                    "end": match.end()
                })
        
        # Look for duration references
        duration_patterns = [
            r'\b(?:for|last|past)\s+(\d+)\s+(?:day|week|month|year)s?\b',  # for X days/weeks/months/years
            r'\b(?:since)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b'  # since Month
        ]
        
        for pattern in duration_patterns:
            for match in re.finditer(pattern, text):
                references.append({
                    "text": match.group(0),
                    "type": "DURATION",
                    "start": match.start(),
                    "end": match.end()
                })
        
        return references 