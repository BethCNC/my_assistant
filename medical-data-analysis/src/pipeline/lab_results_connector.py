"""
Lab Results Pipeline Connector

This module provides integration between the lab result normalizer
and the main ingestion pipeline, enabling specialized processing
of laboratory test results found in medical documents.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.processing.lab_result_normalizer import create_lab_result_normalizer
from src.pipeline.base import PipelineComponent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LabResultsPipelineConnector(PipelineComponent):
    """
    Connector component to integrate lab result normalization
    into the main document processing pipeline.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the lab results pipeline connector.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(name="lab_results_connector")
        self.config = config or {}
        self.lab_normalizer = create_lab_result_normalizer()
    
    def process(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document data to extract and normalize lab results.
        
        Args:
            document_data: Document data dictionary
            
        Returns:
            Updated document data with normalized lab results
        """
        logger.info(f"Processing document for lab results: {document_data.get('file_path', 'unknown')}")
        
        try:
            # Check if document might contain lab results
            if self._might_contain_lab_results(document_data):
                # Process document with lab normalizer
                processed_data = self.lab_normalizer.process_document(document_data)
                
                # Check if lab results were found
                if processed_data.get("processed_data", {}).get("lab_results"):
                    lab_results = processed_data["processed_data"]["lab_results"]
                    logger.info(f"Found {len(lab_results)} lab results in document")
                    
                    # Add additional metadata for downstream processing
                    self._add_lab_metadata(processed_data, lab_results)
                
                return processed_data
            else:
                logger.info(f"Document unlikely to contain lab results, skipping lab extraction")
                return document_data
        except Exception as e:
            logger.error(f"Error in lab results connector: {e}")
            return document_data
    
    def _might_contain_lab_results(self, document_data: Dict[str, Any]) -> bool:
        """
        Determine if a document might contain lab results.
        
        Args:
            document_data: Document data dictionary
            
        Returns:
            True if document might contain lab results, False otherwise
        """
        # Check document type
        document_type = document_data.get("document_type", "").lower()
        if document_type in ["csv", "html"]:
            return True
        
        # Check filename for lab-related keywords
        file_path = document_data.get("file_path", "")
        filename = os.path.basename(file_path).lower()
        lab_keywords = ["lab", "labs", "laboratory", "test", "results", "report", "blood"]
        if any(keyword in filename for keyword in lab_keywords):
            return True
        
        # Check content for lab-related keywords
        content = document_data.get("content", "").lower()
        lab_content_keywords = [
            "lab results", "laboratory results", "test results", 
            "wbc", "rbc", "hemoglobin", "platelet", "glucose", "creatinine",
            "reference range", "reference interval", "normal range",
            "blood test", "chemistry", "hematology"
        ]
        if any(keyword in content for keyword in lab_content_keywords):
            return True
        
        # Check for table structure in HTML
        if document_type == "html" and ("<table" in content and "<tr" in content and "<td" in content):
            return True
        
        return False
    
    def _add_lab_metadata(self, document_data: Dict[str, Any], lab_results: List[Dict[str, Any]]) -> None:
        """
        Add additional metadata based on lab results.
        
        Args:
            document_data: Document data dictionary
            lab_results: List of normalized lab results
        """
        if not lab_results:
            return
        
        # Create metadata if not exists
        if "metadata" not in document_data:
            document_data["metadata"] = {}
        
        # Extract test categories
        test_categories = self._categorize_lab_tests(lab_results)
        document_data["metadata"]["lab_categories"] = list(test_categories.keys())
        
        # Check for abnormal results
        abnormal_results = [result for result in lab_results if result.get("abnormal")]
        if abnormal_results:
            document_data["metadata"]["has_abnormal_results"] = True
            document_data["metadata"]["abnormal_test_count"] = len(abnormal_results)
            
            # Add abnormal test names
            abnormal_test_names = [result["test_name"] for result in abnormal_results]
            document_data["metadata"]["abnormal_tests"] = abnormal_test_names
    
    def _categorize_lab_tests(self, lab_results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Categorize lab tests into medical categories.
        
        Args:
            lab_results: List of normalized lab results
            
        Returns:
            Dictionary mapping categories to test names
        """
        categories = {
            "hematology": [],
            "chemistry": [],
            "lipids": [],
            "thyroid": [],
            "liver": [],
            "kidney": [],
            "electrolytes": [],
            "other": []
        }
        
        # Define test name patterns for each category
        category_patterns = {
            "hematology": [
                "white blood cell", "red blood cell", "hemoglobin", "hematocrit",
                "platelet", "mean corpuscular", "wbc", "rbc", "hgb", "hct", "plt", "mcv", "mch", "mchc"
            ],
            "chemistry": [
                "glucose", "hba1c", "hemoglobin a1c", "vitamin", "ferritin", "iron"
            ],
            "lipids": [
                "cholesterol", "triglyceride", "hdl", "ldl", "vldl", "lipoprotein"
            ],
            "thyroid": [
                "thyroid", "tsh", "t3", "t4", "triiodothyronine", "thyroxine"
            ],
            "liver": [
                "alt", "ast", "ggt", "alkaline phosphatase", "bilirubin", "albumin",
                "alanine", "aspartate", "gamma-glutamyl"
            ],
            "kidney": [
                "creatinine", "urea", "bun", "blood urea nitrogen", "egfr", "estimated glomerular"
            ],
            "electrolytes": [
                "sodium", "potassium", "chloride", "bicarbonate", "carbon dioxide", "calcium",
                "phosphorus", "magnesium", "na", "k", "cl", "co2", "ca"
            ]
        }
        
        # Categorize each test
        for result in lab_results:
            test_name = result["test_name"].lower()
            categorized = False
            
            for category, patterns in category_patterns.items():
                if any(pattern in test_name for pattern in patterns):
                    categories[category].append(result["test_name"])
                    categorized = True
                    break
            
            if not categorized:
                categories["other"].append(result["test_name"])
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

# Factory function for easy instantiation
def create_lab_results_connector(config: Optional[Dict[str, Any]] = None) -> LabResultsPipelineConnector:
    """
    Create a lab results pipeline connector instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured LabResultsPipelineConnector instance
    """
    return LabResultsPipelineConnector(config) 