"""
Lab Result Normalizer Module

This module provides specialized processing for medical lab results,
extracting and normalizing test values, units, and reference ranges.
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LabResultNormalizer:
    """
    Specialized processor for extracting and normalizing laboratory test results
    from medical documents, supporting multiple formats and unit conversions.
    """
    
    # Common lab test unit mappings for normalization
    UNIT_MAPPINGS = {
        # Hematology
        "x10^9/l": "10^9/L",
        "x 10^9/l": "10^9/L",
        "10*9/l": "10^9/L",
        "10^9/l": "10^9/L",
        "10^9/L": "10^9/L",
        "k/ul": "10^9/L",
        "k/µl": "10^9/L",
        "10^3/ul": "10^9/L",
        "10^3/µl": "10^9/L",
        "x10^12/l": "10^12/L",
        "x 10^12/l": "10^12/L",
        "10*12/l": "10^12/L",
        "10^12/l": "10^12/L",
        "10^12/L": "10^12/L",
        "m/ul": "10^12/L",
        "m/µl": "10^12/L",
        "10^6/ul": "10^12/L",
        "10^6/µl": "10^12/L",
        "g/dl": "g/dL",
        "g/dL": "g/dL",
        "g/l": "g/L",
        "g/L": "g/L",
        "%": "%",
        "fl": "fL",
        "fL": "fL",
        "pg": "pg",
        
        # Chemistry
        "mg/dl": "mg/dL",
        "mg/dL": "mg/dL",
        "mg/l": "mg/L",
        "mg/L": "mg/L",
        "ug/dl": "µg/dL",
        "ug/dL": "µg/dL",
        "µg/dl": "µg/dL",
        "µg/dL": "µg/dL",
        "ng/ml": "ng/mL",
        "ng/mL": "ng/mL",
        "pmol/l": "pmol/L",
        "pmol/L": "pmol/L",
        "mmol/l": "mmol/L", 
        "mmol/L": "mmol/L",
        "umol/l": "µmol/L",
        "umol/L": "µmol/L",
        "µmol/l": "µmol/L",
        "µmol/L": "µmol/L",
        "u/l": "U/L",
        "u/L": "U/L",
        "U/l": "U/L",
        "U/L": "U/L",
        "iu/l": "IU/L",
        "iu/L": "IU/L",
        "IU/l": "IU/L",
        "IU/L": "IU/L",
        "meq/l": "mEq/L",
        "meq/L": "mEq/L",
        "mEq/l": "mEq/L",
        "mEq/L": "mEq/L",
    }
    
    # Common test name standardizations
    TEST_NAME_MAPPINGS = {
        # Hematology
        "wbc": "White Blood Cell Count",
        "white blood cell": "White Blood Cell Count",
        "white blood cells": "White Blood Cell Count",
        "white blood cell count": "White Blood Cell Count",
        "white cell count": "White Blood Cell Count",
        "wbc count": "White Blood Cell Count",
        "leukocytes": "White Blood Cell Count",
        
        "rbc": "Red Blood Cell Count",
        "red blood cell": "Red Blood Cell Count",
        "red blood cells": "Red Blood Cell Count",
        "red blood cell count": "Red Blood Cell Count",
        "red cell count": "Red Blood Cell Count",
        "erythrocytes": "Red Blood Cell Count",
        
        "hgb": "Hemoglobin",
        "hb": "Hemoglobin",
        "hemoglobin": "Hemoglobin",
        "haemoglobin": "Hemoglobin",
        
        "hct": "Hematocrit",
        "hematocrit": "Hematocrit",
        "haematocrit": "Hematocrit",
        "pcv": "Hematocrit",
        "packed cell volume": "Hematocrit",
        
        "mcv": "Mean Corpuscular Volume",
        "mean corpuscular volume": "Mean Corpuscular Volume",
        
        "mch": "Mean Corpuscular Hemoglobin",
        "mean corpuscular hemoglobin": "Mean Corpuscular Hemoglobin",
        
        "mchc": "Mean Corpuscular Hemoglobin Concentration",
        "mean corpuscular hemoglobin concentration": "Mean Corpuscular Hemoglobin Concentration",
        
        "plt": "Platelet Count",
        "platelets": "Platelet Count",
        "platelet count": "Platelet Count",
        "thrombocytes": "Platelet Count",
        
        # Chemistry
        "glucose": "Glucose",
        "blood glucose": "Glucose",
        "fasting glucose": "Glucose (Fasting)",
        "fasting blood glucose": "Glucose (Fasting)",
        "fbg": "Glucose (Fasting)",
        
        "bun": "Blood Urea Nitrogen",
        "blood urea nitrogen": "Blood Urea Nitrogen",
        "urea": "Blood Urea Nitrogen",
        
        "creatinine": "Creatinine",
        "creat": "Creatinine",
        
        "sodium": "Sodium",
        "na": "Sodium",
        "na+": "Sodium",
        
        "potassium": "Potassium",
        "k": "Potassium",
        "k+": "Potassium",
        
        "chloride": "Chloride",
        "cl": "Chloride",
        "cl-": "Chloride",
        
        "co2": "Carbon Dioxide",
        "carbon dioxide": "Carbon Dioxide",
        "bicarbonate": "Carbon Dioxide",
        "hco3": "Carbon Dioxide",
        "hco3-": "Carbon Dioxide",
        
        "calcium": "Calcium",
        "ca": "Calcium",
        "ca++": "Calcium",
        
        "phosphorus": "Phosphorus",
        "phosphate": "Phosphorus",
        "phos": "Phosphorus",
        
        "alt": "Alanine Aminotransferase",
        "alanine aminotransferase": "Alanine Aminotransferase",
        "sgpt": "Alanine Aminotransferase",
        
        "ast": "Aspartate Aminotransferase",
        "aspartate aminotransferase": "Aspartate Aminotransferase",
        "sgot": "Aspartate Aminotransferase",
        
        "ggt": "Gamma-Glutamyl Transferase",
        "gamma-glutamyl transferase": "Gamma-Glutamyl Transferase",
        "gamma gt": "Gamma-Glutamyl Transferase",
        
        "alp": "Alkaline Phosphatase",
        "alkaline phosphatase": "Alkaline Phosphatase",
        
        "ldh": "Lactate Dehydrogenase",
        "lactate dehydrogenase": "Lactate Dehydrogenase",
        
        "total bilirubin": "Total Bilirubin",
        "bilirubin total": "Total Bilirubin",
        "bilirubin, total": "Total Bilirubin",
        
        "direct bilirubin": "Direct Bilirubin",
        "bilirubin direct": "Direct Bilirubin",
        "bilirubin, direct": "Direct Bilirubin",
        
        "indirect bilirubin": "Indirect Bilirubin",
        "bilirubin indirect": "Indirect Bilirubin",
        "bilirubin, indirect": "Indirect Bilirubin",
        
        "total protein": "Total Protein",
        "protein total": "Total Protein",
        "protein, total": "Total Protein",
        
        "albumin": "Albumin",
        "alb": "Albumin",
        
        "globulin": "Globulin",
        "glob": "Globulin",
        
        "a/g ratio": "Albumin/Globulin Ratio",
        "albumin/globulin ratio": "Albumin/Globulin Ratio",
        
        "total cholesterol": "Total Cholesterol",
        "cholesterol total": "Total Cholesterol",
        "cholesterol, total": "Total Cholesterol",
        
        "triglycerides": "Triglycerides",
        "tg": "Triglycerides",
        
        "hdl": "HDL Cholesterol",
        "hdl cholesterol": "HDL Cholesterol",
        "hdl-c": "HDL Cholesterol",
        
        "ldl": "LDL Cholesterol",
        "ldl cholesterol": "LDL Cholesterol",
        "ldl-c": "LDL Cholesterol",
        
        "vldl": "VLDL Cholesterol",
        "vldl cholesterol": "VLDL Cholesterol",
        "vldl-c": "VLDL Cholesterol",
        
        "ferritin": "Ferritin",
        
        "iron": "Iron",
        "fe": "Iron",
        
        "tibc": "Total Iron Binding Capacity",
        "total iron binding capacity": "Total Iron Binding Capacity",
        
        "transferrin": "Transferrin",
        
        "tsh": "Thyroid Stimulating Hormone",
        "thyroid stimulating hormone": "Thyroid Stimulating Hormone",
        
        "t3": "Triiodothyronine (T3)",
        "triiodothyronine": "Triiodothyronine (T3)",
        "total t3": "Triiodothyronine (T3)",
        
        "t4": "Thyroxine (T4)",
        "thyroxine": "Thyroxine (T4)",
        "total t4": "Thyroxine (T4)",
        
        "free t3": "Free Triiodothyronine (Free T3)",
        "ft3": "Free Triiodothyronine (Free T3)",
        
        "free t4": "Free Thyroxine (Free T4)",
        "ft4": "Free Thyroxine (Free T4)",
    }
    
    def __init__(self):
        """Initialize the lab result normalizer."""
        self.test_name_pattern = re.compile(r'([a-zA-Z0-9\s,\-\(\)]+)[\s:]*([\d\.]+)[\s]*([\w\%\/\^]+)?(?:\s*\(?([\d\.\-\s]+)?\)?)?')
        self.range_pattern = re.compile(r'([\d\.]+)\s*-\s*([\d\.]+)')
    
    def normalize_lab_results(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract and normalize lab results from text content.
        
        Args:
            content: The text content containing lab results
            
        Returns:
            List of normalized lab results
        """
        normalized_results = []
        
        # Split content into lines
        lines = content.strip().split('\n')
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Try to match lab result pattern
            matches = self.test_name_pattern.findall(line)
            
            for match in matches:
                test_name, value, unit, reference_range = match
                
                # Skip if no test name or value
                if not test_name.strip() or not value.strip():
                    continue
                
                # Normalize test name
                normalized_test_name = self._normalize_test_name(test_name.strip().lower())
                
                # Normalize value
                try:
                    normalized_value = float(value.strip())
                except ValueError:
                    normalized_value = value.strip()
                
                # Normalize unit
                normalized_unit = self._normalize_unit(unit.strip().lower() if unit else "")
                
                # Parse reference range
                low_ref, high_ref = self._parse_reference_range(reference_range)
                
                # Create normalized result
                normalized_result = {
                    "test_name": normalized_test_name,
                    "original_test_name": test_name.strip(),
                    "value": normalized_value,
                    "unit": normalized_unit,
                    "reference_range": {
                        "low": low_ref,
                        "high": high_ref,
                        "original": reference_range.strip() if reference_range else None
                    },
                    "abnormal": self._is_abnormal(normalized_value, low_ref, high_ref)
                }
                
                normalized_results.append(normalized_result)
        
        return normalized_results
    
    def normalize_tabular_lab_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and normalize lab results from tabular data.
        
        Args:
            data: Dictionary containing test names, values, units, and reference ranges
            
        Returns:
            List of normalized lab results
        """
        normalized_results = []
        
        # Extract data from dictionary
        test_names = data.get("test_names", [])
        values = data.get("values", [])
        units = data.get("units", [])
        reference_ranges = data.get("reference_ranges", [])
        
        # Ensure all lists have the same length by padding with None
        max_length = max(len(test_names), len(values), len(units), len(reference_ranges))
        test_names = test_names + [None] * (max_length - len(test_names))
        values = values + [None] * (max_length - len(values))
        units = units + [None] * (max_length - len(units))
        reference_ranges = reference_ranges + [None] * (max_length - len(reference_ranges))
        
        for i in range(max_length):
            test_name = test_names[i]
            value = values[i]
            unit = units[i]
            reference_range = reference_ranges[i]
            
            # Skip if no test name or value
            if not test_name or value is None:
                continue
            
            # Normalize test name
            normalized_test_name = self._normalize_test_name(str(test_name).strip().lower())
            
            # Normalize value
            try:
                normalized_value = float(value)
            except (ValueError, TypeError):
                normalized_value = str(value).strip()
            
            # Normalize unit
            normalized_unit = self._normalize_unit(str(unit).strip().lower() if unit else "")
            
            # Parse reference range
            low_ref, high_ref = self._parse_reference_range(str(reference_range) if reference_range else None)
            
            # Create normalized result
            normalized_result = {
                "test_name": normalized_test_name,
                "original_test_name": str(test_name).strip(),
                "value": normalized_value,
                "unit": normalized_unit,
                "reference_range": {
                    "low": low_ref,
                    "high": high_ref,
                    "original": str(reference_range).strip() if reference_range else None
                },
                "abnormal": self._is_abnormal(normalized_value, low_ref, high_ref)
            }
            
            normalized_results.append(normalized_result)
        
        return normalized_results
    
    def _normalize_test_name(self, test_name: str) -> str:
        """
        Normalize test name using standard mappings.
        
        Args:
            test_name: Original test name
            
        Returns:
            Normalized test name
        """
        # Remove common suffixes and prefixes
        clean_name = test_name.replace("test", "").replace("level", "").strip()
        
        # Apply standard mappings
        for pattern, standard_name in self.TEST_NAME_MAPPINGS.items():
            if clean_name == pattern or clean_name.startswith(pattern + " ") or clean_name.endswith(" " + pattern):
                return standard_name
        
        # Return original if no mapping found
        return test_name.title()
    
    def _normalize_unit(self, unit: str) -> str:
        """
        Normalize unit using standard mappings.
        
        Args:
            unit: Original unit
            
        Returns:
            Normalized unit
        """
        if not unit:
            return ""
            
        # Apply standard mappings
        for pattern, standard_unit in self.UNIT_MAPPINGS.items():
            if unit == pattern:
                return standard_unit
        
        # Return original if no mapping found
        return unit
    
    def _parse_reference_range(self, reference_range: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse reference range string into low and high values.
        
        Args:
            reference_range: Reference range string (e.g., "3.5-5.0")
            
        Returns:
            Tuple of (low, high) reference values
        """
        if not reference_range:
            return None, None
        
        # Try to match range pattern
        match = self.range_pattern.search(reference_range)
        
        if match:
            try:
                low_ref = float(match.group(1))
                high_ref = float(match.group(2))
                return low_ref, high_ref
            except ValueError:
                pass
        
        return None, None
    
    def _is_abnormal(
        self, 
        value: Union[float, str], 
        low_ref: Optional[float], 
        high_ref: Optional[float]
    ) -> Optional[bool]:
        """
        Determine if a value is abnormal based on reference range.
        
        Args:
            value: Test value
            low_ref: Low reference value
            high_ref: High reference value
            
        Returns:
            True if abnormal, False if normal, None if can't determine
        """
        if not isinstance(value, (int, float)):
            return None
        
        if low_ref is not None and high_ref is not None:
            return value < low_ref or value > high_ref
        
        return None
    
    def extract_from_html_table(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract lab results from HTML tables.
        
        Args:
            html_content: HTML content containing lab result tables
            
        Returns:
            List of normalized lab results
        """
        try:
            # Read HTML tables
            tables = pd.read_html(html_content)
            
            normalized_results = []
            
            for table in tables:
                # Check if table might contain lab results
                if len(table.columns) < 2:
                    continue
                
                # Try to identify column roles based on headers
                column_roles = self._identify_table_columns(table)
                
                if not column_roles.get("test_name") or not column_roles.get("value"):
                    continue
                
                # Extract data from table
                for _, row in table.iterrows():
                    try:
                        test_name = row[column_roles["test_name"]]
                        value = row[column_roles["value"]]
                        
                        # Skip if test name or value is missing
                        if pd.isna(test_name) or pd.isna(value):
                            continue
                        
                        unit = row[column_roles["unit"]] if column_roles.get("unit") else ""
                        reference_range = row[column_roles["reference_range"]] if column_roles.get("reference_range") else ""
                        
                        # Handle NaN values
                        if pd.isna(unit):
                            unit = ""
                        if pd.isna(reference_range):
                            reference_range = ""
                        
                        # Normalize test name
                        normalized_test_name = self._normalize_test_name(str(test_name).strip().lower())
                        
                        # Normalize value
                        try:
                            normalized_value = float(value)
                        except (ValueError, TypeError):
                            normalized_value = str(value).strip()
                        
                        # Normalize unit
                        normalized_unit = self._normalize_unit(str(unit).strip().lower())
                        
                        # Parse reference range
                        low_ref, high_ref = self._parse_reference_range(str(reference_range))
                        
                        # Create normalized result
                        normalized_result = {
                            "test_name": normalized_test_name,
                            "original_test_name": str(test_name).strip(),
                            "value": normalized_value,
                            "unit": normalized_unit,
                            "reference_range": {
                                "low": low_ref,
                                "high": high_ref,
                                "original": str(reference_range).strip()
                            },
                            "abnormal": self._is_abnormal(normalized_value, low_ref, high_ref)
                        }
                        
                        normalized_results.append(normalized_result)
                    except Exception as e:
                        logger.error(f"Error processing table row: {e}")
            
            return normalized_results
        except Exception as e:
            logger.error(f"Error extracting lab results from HTML: {e}")
            return []
    
    def _identify_table_columns(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify the roles of columns in a lab result table.
        
        Args:
            table: DataFrame containing the table
            
        Returns:
            Dictionary mapping column roles to column indices
        """
        column_roles = {}
        
        # Convert column names to strings
        columns = [str(col).lower() for col in table.columns]
        
        # Identify test name column
        test_name_keywords = ["test", "parameter", "analyte", "component", "examination", "determination"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in test_name_keywords):
                column_roles["test_name"] = table.columns[i]
                break
        
        # If no test name column found, assume first column
        if "test_name" not in column_roles and len(table.columns) > 0:
            column_roles["test_name"] = table.columns[0]
        
        # Identify value column
        value_keywords = ["result", "value", "measurement", "observed"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in value_keywords):
                column_roles["value"] = table.columns[i]
                break
        
        # If no value column found, assume second column
        if "value" not in column_roles and len(table.columns) > 1:
            column_roles["value"] = table.columns[1]
        
        # Identify unit column
        unit_keywords = ["unit", "units"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in unit_keywords):
                column_roles["unit"] = table.columns[i]
                break
        
        # Identify reference range column
        reference_keywords = ["reference", "range", "normal", "interval", "expected"]
        for i, col in enumerate(columns):
            if any(keyword in col for keyword in reference_keywords):
                column_roles["reference_range"] = table.columns[i]
                break
        
        return column_roles
    
    def process_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document to extract and normalize lab results.
        
        Args:
            document_data: Document data dictionary
            
        Returns:
            Updated document data with normalized lab results
        """
        try:
            # Extract content from document
            content = document_data.get("content", "")
            document_type = document_data.get("document_type", "")
            
            normalized_results = []
            
            # Process based on document type
            if document_type == "html" or content.strip().startswith("<"):
                # Extract from HTML
                normalized_results = self.extract_from_html_table(content)
            elif document_type == "csv":
                # Extract from CSV-like data
                if "structured_data" in document_data:
                    normalized_results = self.normalize_tabular_lab_results(document_data["structured_data"])
            else:
                # Extract from text
                normalized_results = self.normalize_lab_results(content)
            
            # Add normalized results to document data
            if normalized_results:
                if "processed_data" not in document_data:
                    document_data["processed_data"] = {}
                
                document_data["processed_data"]["lab_results"] = normalized_results
                
                # Add metadata about lab results
                document_data["metadata"] = document_data.get("metadata", {})
                document_data["metadata"]["contains_lab_results"] = True
                document_data["metadata"]["lab_test_count"] = len(normalized_results)
                
                # Count abnormal results
                abnormal_count = sum(1 for result in normalized_results if result.get("abnormal"))
                document_data["metadata"]["abnormal_lab_count"] = abnormal_count
            
            return document_data
        except Exception as e:
            logger.error(f"Error processing document for lab results: {e}")
            return document_data


# Create a factory function for easy instantiation
def create_lab_result_normalizer() -> LabResultNormalizer:
    """
    Create a lab result normalizer instance.
    
    Returns:
        Configured LabResultNormalizer instance
    """
    return LabResultNormalizer() 