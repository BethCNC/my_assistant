from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
import logging
import re
from datetime import datetime

class BaseProcessor(ABC):
    """Base abstract class for data processors that clean and normalize extracted medical data."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data = {}
        
        # Common date format patterns
        self.date_formats = [
            '%Y-%m-%d',       # 2023-01-15
            '%m/%d/%Y',       # 01/15/2023
            '%d/%m/%Y',       # 15/01/2023
            '%m-%d-%Y',       # 01-15-2023
            '%d-%m-%Y',       # 15-01-2023
            '%Y/%m/%d',       # 2023/01/15
            '%b %d, %Y',      # Jan 15, 2023
            '%d %b %Y',       # 15 Jan 2023
            '%B %d, %Y',      # January 15, 2023
            '%d %B %Y',       # 15 January 2023
            '%m/%d/%y',       # 01/15/23
            '%d/%m/%y',       # 15/01/23
        ]
        
        # Patterns for medical specialties and departments
        self.specialties = {
            'rheumatology': ['rheumatology', 'rheumatologist', 'arthritis', 'joints', 'connective tissue'],
            'neurology': ['neurology', 'neurologist', 'brain', 'nerve', 'spinal', 'seizure', 'migraine'],
            'cardiology': ['cardiology', 'cardiologist', 'heart', 'cardiac', 'ecg', 'echocardiogram'],
            'gastroenterology': ['gastroenterology', 'gastroenterologist', 'stomach', 'intestine', 'colon', 'bowel'],
            'endocrinology': ['endocrinology', 'endocrinologist', 'hormone', 'thyroid', 'diabetes'],
            'psychiatry': ['psychiatry', 'psychiatrist', 'mental health', 'depression', 'anxiety', 'adhd'],
            'genetics': ['genetics', 'geneticist', 'dna', 'chromosome', 'mutation'],
            'immunology': ['immunology', 'immunologist', 'allergy', 'immune', 'autoimmune'],
            'dermatology': ['dermatology', 'dermatologist', 'skin', 'rash', 'eczema'],
            'orthopedics': ['orthopedics', 'orthopedist', 'bone', 'joint', 'fracture', 'spine'],
            'primary care': ['primary care', 'family medicine', 'general practice', 'internist', 'family physician'],
        }
        
        # Patterns for specific conditions
        self.condition_patterns = {
            'eds': ['ehlers-danlos', 'ehlers danlos', 'hypermobility', 'eds', 'heds', 'eds-ht', 'joint hypermobility', 'skin elasticity', 'hypermobile', 'beighton'],
            'pots': ['pots', 'postural orthostatic tachycardia', 'dysautonomia', 'orthostatic intolerance', 'tachycardia', 'postural tachycardia'],
            'mcas': ['mcas', 'mast cell activation', 'mast cell', 'histamine', 'mastocytosis', 'mast cell mediator'],
            'asd': ['autism', 'autistic', 'asd', 'asperger', 'neurodivergent', 'sensory processing', 'stimming', 'special interest', 'social communication', 'repetitive behavior', 'overstimulation'],
            'adhd': ['adhd', 'attention deficit', 'hyperactivity', 'executive function', 'impulsivity', 'inattention', 'dopamine', 'executive dysfunction'],
            'chronic pain': ['chronic pain', 'fibromyalgia', 'myalgia', 'pain syndrome', 'constant pain', 'persistent pain', 'pain management'],
        }
    
    def process(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the extracted data. Common processing for all document types.
        
        Args:
            extracted_data: Dictionary containing extracted document data
            
        Returns:
            Dictionary with processed document data
        """
        self.data = extracted_data.copy()
        
        # Normalize dates
        self.data["normalized_dates"] = self.normalize_dates(
            self.data.get("extracted_dates", set())
        )
        
        # Identify medical specialties
        self.data["medical_specialties"] = self.identify_specialties(
            self.data.get("content", "")
        )
        
        # Categorize conditions
        self.data["condition_categories"] = self.categorize_conditions(
            self.data.get("content", "")
        )
        
        # Run specialized processing in child classes
        self.specialized_processing()
        
        return self.data
    
    def normalize_dates(self, date_strings: Set[str]) -> List[Dict[str, Any]]:
        """
        Normalize dates to ISO format.
        
        Args:
            date_strings: Set of date strings
            
        Returns:
            List of dictionaries with normalized dates
        """
        normalized_dates = []
        
        for date_str in date_strings:
            for fmt in self.date_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    normalized_dates.append({
                        "original": date_str,
                        "iso_date": date_obj.strftime("%Y-%m-%d"),
                        "year": date_obj.year,
                        "month": date_obj.month,
                        "day": date_obj.day
                    })
                    break  # If successful, no need to try other formats
                except ValueError:
                    continue
                    
        return normalized_dates
    
    def identify_specialties(self, text: str) -> Dict[str, float]:
        """
        Identify medical specialties mentioned in the text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary mapping specialties to confidence scores
        """
        text = text.lower()
        specialty_scores = {}
        
        for specialty, keywords in self.specialties.items():
            matches = 0
            for keyword in keywords:
                matches += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
            
            if matches > 0:
                confidence = min(matches / len(keywords) * 0.5, 1.0)  # Scale confidence
                specialty_scores[specialty] = round(confidence, 2)
                
        return specialty_scores
    
    def categorize_conditions(self, text: str) -> Dict[str, List[str]]:
        """
        Categorize conditions mentioned in the text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary mapping condition categories to terms found
        """
        text = text.lower()
        condition_matches = {}
        
        for condition, patterns in self.condition_patterns.items():
            matches = []
            for pattern in patterns:
                # Find all instances of this pattern in the text
                for match in re.finditer(r'\b' + re.escape(pattern) + r'\b', text):
                    # Get some context around the match (up to 100 chars)
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    
                    # Only add unique matches with context
                    if match.group() not in [m.get("term") for m in matches]:
                        matches.append({
                            "term": match.group(),
                            "context": context.strip(),
                            "position": match.start()
                        })
            
            if matches:
                condition_matches[condition] = [match["term"] for match in matches]
                
        return condition_matches
    
    @abstractmethod
    def specialized_processing(self) -> None:
        """
        Implement specialized processing logic in child classes.
        This method should enhance self.data with additional processed information.
        """
        pass
    
    def normalize_medical_terms(self, terms: List[str]) -> List[str]:
        """
        Normalize medical terminology to standard formats.
        
        Args:
            terms: List of medical terms to normalize
            
        Returns:
            List of normalized medical terms
        """
        normalized_terms = []
        
        for term in terms:
            term = term.strip().lower()
            
            # Basic normalization rules
            # 1. Remove trailing periods
            term = re.sub(r'\.$', '', term)
            
            # 2. Standardize common abbreviations
            term_mappings = {
                'dx': 'diagnosis',
                'hx': 'history',
                'tx': 'treatment',
                'rx': 'prescription',
                'meds': 'medications',
                'labs': 'laboratory tests',
                'bp': 'blood pressure',
                'hr': 'heart rate',
                'temp': 'temperature',
                'pt': 'patient',
                'f/u': 'follow up',
                'w/': 'with',
                'w/o': 'without',
                'neg': 'negative',
                'pos': 'positive',
                'abd': 'abdominal',
                'bilat': 'bilateral',
            }
            
            # Apply mappings for exact matches only
            if term in term_mappings:
                term = term_mappings[term]
            
            normalized_terms.append(term)
        
        return normalized_terms
        
    def remove_duplicates(self, items: List[Any]) -> List[Any]:
        """
        Remove duplicate items while preserving order.
        
        Args:
            items: List of items to deduplicate
            
        Returns:
            Deduplicated list with original order preserved
        """
        seen = set()
        unique_items = []
        
        for item in items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
                
        return unique_items 