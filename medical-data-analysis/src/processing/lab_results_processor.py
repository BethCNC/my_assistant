import re
from typing import Dict, List, Any, Optional, Tuple
import logging

from src.processing.base import BaseProcessor

class LabResultsProcessor(BaseProcessor):
    """Specialized processor for lab test results with reference range handling."""
    
    def __init__(self):
        super().__init__()
        
        # Lab test patterns with value and reference ranges
        self.lab_test_pattern = re.compile(
            r'\b([A-Za-z\s\-]+):\s*(\d+\.?\d*)\s*([a-zA-Z/%]+)?\s*(?:\((?:Reference|Normal)(?:\s+Range)?:\s*([<>]?\s*\d+\.?\d*(?:\s*-\s*\d+\.?\d*)?)\s*([a-zA-Z/%]+)?\)?)?',
            re.IGNORECASE
        )
        
        # Common lab test name normalizations
        self.lab_test_normalizations = {
            # Blood counts
            "wbc": "white blood cell count",
            "rbc": "red blood cell count",
            "hgb": "hemoglobin",
            "hct": "hematocrit",
            "plt": "platelet count",
            
            # Metabolic panel
            "glu": "glucose",
            "bun": "blood urea nitrogen",
            "cr": "creatinine",
            "na": "sodium",
            "k": "potassium",
            "cl": "chloride",
            "co2": "carbon dioxide",
            "ca": "calcium",
            
            # Lipid panel
            "chol": "cholesterol",
            "hdl": "hdl cholesterol",
            "ldl": "ldl cholesterol",
            "trig": "triglycerides",
            
            # Liver function
            "alt": "alanine aminotransferase",
            "ast": "aspartate aminotransferase",
            "alp": "alkaline phosphatase",
            "tbil": "total bilirubin",
            
            # Thyroid
            "tsh": "thyroid stimulating hormone",
            "ft4": "free t4",
            "ft3": "free t3",
            
            # Other common tests
            "a1c": "hemoglobin a1c",
            "esr": "erythrocyte sedimentation rate",
            "crp": "c-reactive protein",
            "rfactor": "rheumatoid factor",
            "ana": "antinuclear antibody",
        }
        
        # Lab test categories mapping
        self.test_categories = {
            "complete blood count": [
                "white blood cell count", "red blood cell count", "hemoglobin", 
                "hematocrit", "platelet count", "mcv", "mch", "mchc", "rdw",
                "neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils"
            ],
            "basic metabolic panel": [
                "glucose", "blood urea nitrogen", "creatinine", "sodium", 
                "potassium", "chloride", "carbon dioxide", "calcium"
            ],
            "lipid panel": [
                "cholesterol", "hdl cholesterol", "ldl cholesterol", 
                "triglycerides", "vldl cholesterol"
            ],
            "liver function": [
                "alanine aminotransferase", "aspartate aminotransferase", 
                "alkaline phosphatase", "total bilirubin", "direct bilirubin",
                "albumin", "total protein", "ggt"
            ],
            "thyroid panel": [
                "thyroid stimulating hormone", "free t4", "free t3", 
                "total t4", "total t3", "thyroid peroxidase antibody"
            ],
            "inflammatory markers": [
                "c-reactive protein", "erythrocyte sedimentation rate", 
                "ferritin", "procalcitonin"
            ],
            "connective tissue disorder markers": [
                "antinuclear antibody", "rheumatoid factor", "anti-ccp antibody",
                "anti-dsdna", "anti-sm", "anti-ro", "anti-la", "c3 complement",
                "c4 complement"
            ],
            "vitamin levels": [
                "vitamin d", "vitamin b12", "folate", "vitamin b6"
            ]
        }
    
    def process(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process extracted lab result data, normalizing test names and values.
        
        Args:
            extracted_data: Dictionary containing extracted raw data
            
        Returns:
            Dictionary with processed and normalized lab results data
        """
        processed_data = {
            "metadata": extracted_data.get("metadata", {}),
            "content": extracted_data.get("content", ""),
            "normalized_dates": [],
            "lab_results": [],
            "lab_results_by_category": {},
            "raw_lab_results": extracted_data.get("lab_results", []),
        }
        
        # Process and normalize dates
        if "dates" in extracted_data:
            processed_data["normalized_dates"] = self.normalize_dates(extracted_data["dates"])
        
        # Extract lab results from raw content
        if processed_data["content"]:
            lab_results = self.extract_lab_results(processed_data["content"])
            processed_data["lab_results"] = lab_results
        
        # Also include any pre-extracted lab results from the extractor
        if processed_data["raw_lab_results"]:
            for lab_result in processed_data["raw_lab_results"]:
                # Try to convert pre-extracted lab results to our standardized format
                normalized_lab_result = self.normalize_lab_result(
                    lab_result.get("test_name", ""),
                    lab_result.get("value", ""),
                    lab_result.get("unit", ""),
                    lab_result.get("reference_range", "")
                )
                
                if normalized_lab_result:
                    processed_data["lab_results"].append(normalized_lab_result)
        
        # Categorize lab results by test category
        processed_data["lab_results_by_category"] = self.categorize_lab_results(processed_data["lab_results"])
        
        return processed_data
    
    def extract_lab_results(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract lab test results from text with reference ranges.
        
        Args:
            text: Lab result text content
            
        Returns:
            List of dictionaries with normalized lab result details
        """
        lab_results = []
        
        for match in self.lab_test_pattern.finditer(text):
            test_name = match.group(1).strip()
            value = match.group(2)
            unit = match.group(3) if match.group(3) else ""
            reference_range = match.group(4) if match.group(4) else ""
            reference_unit = match.group(5) if match.group(5) else unit
            
            # Normalize the lab result
            normalized_result = self.normalize_lab_result(test_name, value, unit, reference_range, reference_unit)
            
            if normalized_result:
                lab_results.append(normalized_result)
        
        return lab_results
    
    def normalize_lab_result(self, test_name: str, value: str, unit: str = "", 
                            reference_range: str = "", reference_unit: str = "") -> Optional[Dict[str, Any]]:
        """
        Normalize a lab test result with standardized test names and units.
        
        Args:
            test_name: Raw test name
            value: Test value
            unit: Value unit
            reference_range: Reference/normal range
            reference_unit: Unit for the reference range
            
        Returns:
            Normalized lab result dictionary or None if invalid
        """
        if not test_name or not value:
            return None
        
        # Clean and normalize test name
        test_name = test_name.lower().strip()
        normalized_name = self.lab_test_normalizations.get(test_name, test_name)
        
        # Create normalized result structure
        normalized_result = {
            "test_name": normalized_name,
            "value": value,
            "unit": unit.strip(),
            "reference_range": reference_range.strip(),
            "reference_unit": reference_unit.strip(),
            "is_abnormal": False,
            "trend": "stable",
            "original_test_name": test_name,
        }
        
        # Try to determine if the value is abnormal based on reference range
        if reference_range:
            normalized_result["is_abnormal"] = self.check_if_abnormal(value, reference_range)
        
        return normalized_result
    
    def check_if_abnormal(self, value: str, reference_range: str) -> bool:
        """
        Check if a lab value is outside the reference range.
        
        Args:
            value: The numeric value to check
            reference_range: The reference range string (e.g., '10-20', '<10', '>5')
            
        Returns:
            True if the value is abnormal, False otherwise
        """
        try:
            numeric_value = float(value)
            
            # Handle ranges with hyphens (e.g., "10-20")
            if '-' in reference_range:
                range_parts = reference_range.split('-')
                min_value = float(range_parts[0].strip())
                max_value = float(range_parts[1].strip())
                return numeric_value < min_value or numeric_value > max_value
            
            # Handle greater than ranges (e.g., ">5")
            elif '>' in reference_range:
                threshold = float(reference_range.replace('>', '').strip())
                return numeric_value <= threshold
            
            # Handle less than ranges (e.g., "<10")
            elif '<' in reference_range:
                threshold = float(reference_range.replace('<', '').strip())
                return numeric_value >= threshold
            
            # Single value (e.g., "5")
            else:
                threshold = float(reference_range.strip())
                return numeric_value != threshold
                
        except (ValueError, IndexError):
            # If we can't parse the value or reference range, default to not abnormal
            return False
    
    def specialized_processing(self) -> None:
        """
        Implement specialized processing for lab results as required by BaseProcessor.
        This enhances self.data with additional processed lab information.
        """
        if not self.data.get("content"):
            return
            
        content = self.data.get("content", "")
        
        # Extract lab results from raw content if not already present
        if "lab_results" not in self.data:
            self.data["lab_results"] = self.extract_lab_results(content)
            
        # Process any pre-extracted lab results from the extractor
        if "raw_lab_results" in self.data and self.data["raw_lab_results"]:
            for lab_result in self.data["raw_lab_results"]:
                # Try to convert pre-extracted lab results to our standardized format
                normalized_lab_result = self.normalize_lab_result(
                    lab_result.get("test_name", ""),
                    lab_result.get("value", ""),
                    lab_result.get("unit", ""),
                    lab_result.get("reference_range", "")
                )
                
                if normalized_lab_result:
                    self.data["lab_results"].append(normalized_lab_result)
        
        # Categorize lab results by test category
        self.data["lab_results_by_category"] = self.categorize_lab_results(
            self.data.get("lab_results", [])
        )
            
    def categorize_lab_results(self, lab_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize lab results by category.
        
        Args:
            lab_results: List of normalized lab results
            
        Returns:
            Dictionary with lab results organized by test category
        """
        categorized_results = {category: [] for category in self.test_categories}
        categorized_results["other"] = []  # For tests that don't match a category
        
        for lab_result in lab_results:
            test_name = lab_result["test_name"].lower()
            
            # Check each category to see if the test belongs
            categorized = False
            for category, tests in self.test_categories.items():
                for test in tests:
                    if test in test_name or test_name in test:
                        categorized_results[category].append(lab_result)
                        categorized = True
                        break
                
                if categorized:
                    break
            
            # If not categorized, add to "other"
            if not categorized:
                categorized_results["other"].append(lab_result)
        
        # Remove empty categories
        return {k: v for k, v in categorized_results.items() if v} 