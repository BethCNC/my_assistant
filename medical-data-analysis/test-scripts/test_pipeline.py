#!/usr/bin/env python3
"""
End-to-End Medical Data Pipeline Test

This script tests the complete functionality of the medical data ingestion pipeline
including file processing, AI analysis, and vector database integration.
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Create test directories and sample test files."""
    # Create necessary directories
    dirs = [
        "input/pdf_documents",
        "input/text_documents",
        "input/html_documents",
        "input/csv_data",
        "processed_data/file_registry",
        "processed_data/reports",
        "processed_data/errors",
        "vectordb"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create a sample text document for testing
    sample_text = """
    Patient Medical Record - EDS Assessment
    Date: 2023-05-15
    
    Patient reports joint hypermobility affecting multiple joints including fingers, 
    wrists, elbows, and knees. Patient scores 7/9 on the Beighton scale.
    
    Current medications include:
    - Celebrex 200mg daily for pain management
    - Vitamin D3 5000 IU daily
    
    Patient also reports chronic fatigue and occasional heart palpitations.
    
    Assessment: Patient meets criteria for hypermobile Ehlers-Danlos Syndrome (hEDS)
    based on 2017 diagnostic criteria.
    
    Plan:
    1. Referral to physical therapy for joint stabilization
    2. Consider POTS evaluation based on reported palpitations
    3. Follow up in 3 months
    """
    
    test_file_path = "input/text_documents/sample_eds_assessment.txt"
    with open(test_file_path, "w") as f:
        f.write(sample_text)
    
    logger.info(f"Created test file: {test_file_path}")
    
    return test_file_path

def cleanup_test_environment(test_file_path):
    """Clean up test files after test completes."""
    try:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            logger.info(f"Removed test file: {test_file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up test file: {e}")

def test_pipeline_initialization():
    """Test that the pipeline can be initialized."""
    logger.info("=== Testing Pipeline Initialization ===")
    
    try:
        # Initialize the pipeline with correct parameters
        from src.pipeline.ingestion_pipeline import IngestionPipeline
        
        pipeline = IngestionPipeline(
            input_dir=None,
            output_dir=None,
            processed_dir="processed_data",
            models_dir=None,
            session=None,
            use_gpu=False
        )
        logger.info("✓ Successfully initialized pipeline")
        return pipeline
    except Exception as e:
        logger.error(f"Error initializing pipeline: {e}")
        return None

def test_file_processing(pipeline, test_file_path):
    """Test processing a file through the pipeline."""
    if pipeline is None:
        logger.error("Pipeline not initialized, skipping file processing test")
        return False
    
    try:
        logger.info(f"Processing test file: {test_file_path}")
        result = pipeline.process_file(test_file_path)
        
        # Check if processing was successful
        if result is None:
            logger.error("File processing returned None")
            return False
        
        if "error" in result:
            logger.error(f"Error processing file: {result['error']}")
            return False
        
        logger.info(f"Successfully processed file")
        
        # Check for expected keys in result
        expected_keys = ["metadata", "content", "ai_analysis"]
        for key in expected_keys:
            if key not in result:
                logger.warning(f"Expected key '{key}' not found in processing result")
        
        # Print summary of extracted entities if available
        if "ai_analysis" in result and "entities" in result["ai_analysis"]:
            entities = result["ai_analysis"]["entities"]
            entity_counts = {}
            for entity in entities:
                entity_type = entity["type"]
                if entity_type not in entity_counts:
                    entity_counts[entity_type] = 0
                entity_counts[entity_type] += 1
            
            logger.info(f"Extracted entities: {entity_counts}")
        
        # Check if vector DB information was added
        if "vector_db" in result:
            vector_info = result["vector_db"]
            if "document_vector_id" in vector_info:
                logger.info(f"Document vector ID: {vector_info['document_vector_id']}")
            else:
                logger.warning("No document vector ID in result")
            
            if "entity_vector_ids" in vector_info:
                entity_vectors = vector_info["entity_vector_ids"]
                logger.info(f"Entity vectors: {list(entity_vectors.keys())}")
            else:
                logger.warning("No entity vectors in result")
        else:
            logger.warning("No vector DB information in result")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during file processing: {e}")
        return False

def test_vector_search():
    """Test vector searching functionality."""
    try:
        from src.ai.vectordb.medical_vector_store import MedicalVectorStore
        
        vector_store = MedicalVectorStore(
            storage_path="vectordb",
            use_gpu=False
        )
        
        # Try to search for documents
        search_query = "Ehlers-Danlos joint hypermobility"
        logger.info(f"Searching for: '{search_query}'")
        
        results = vector_store.search(search_query, limit=3)
        
        if len(results) > 0:
            logger.info(f"Found {len(results)} matching documents/entities")
            for i, result in enumerate(results):
                logger.info(f"  {i+1}. Type: {result['entity_type']}, Score: {result['similarity']:.4f}")
            return True
        else:
            logger.warning("No search results found")
            return False
    
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        return False

def test_pipeline_through_dag():
    """Test the pipeline through DAG execution."""
    logger.info("=== Testing Pipeline through DAG ===")
    
    try:
        # Attempt to import airflow components
        try:
            from airflow import DAG
            from airflow.utils.dates import days_ago
            from airflow.operators.python import PythonOperator
            airflow_available = True
        except ImportError:
            logger.warning("Airflow not installed. Skipping DAG execution test.")
            airflow_available = False
            return False
        
        # Only proceed if airflow is available
        if airflow_available:
            from dags.medical_data_ingestion_dag import detect_new_files, process_files
            
            # Create test context for task instance
            context = {
                'ti': MockTaskInstance(),
                'ds': '2023-04-30',
                'dag': MockDAG()
            }
            
            # Run the pipeline through the DAG
            detect_new_files(**context)
            process_files(**context)
            
            logger.info("Successfully executed pipeline through DAG")
            return True
    except Exception as e:
        logger.error(f"Error running pipeline from DAG: {str(e)}")
        return False

def run_all_tests():
    """Run all pipeline tests."""
    test_results = {}
    test_file_path = None
    
    try:
        # Setup test environment
        test_file_path = setup_test_environment()
        
        # Test pipeline initialization
        logger.info("=== Testing Pipeline Initialization ===")
        pipeline = test_pipeline_initialization()
        test_results["pipeline_initialization"] = pipeline is not None
        
        # Test file processing
        logger.info("=== Testing File Processing ===")
        test_results["file_processing"] = test_file_processing(pipeline, test_file_path)
        
        # Clean up pipeline resources
        if pipeline is not None:
            pipeline.close()
        
        # Test vector search
        logger.info("=== Testing Vector Search ===")
        test_results["vector_search"] = test_vector_search()
        
        # Test running through DAG
        logger.info("=== Testing Pipeline through DAG ===")
        test_results["dag_execution"] = test_pipeline_through_dag()
        
        # Calculate overall success
        overall_success = all(test_results.values())
        
        # Log summary
        logger.info("=== Test Results Summary ===")
        for test_name, result in test_results.items():
            logger.info(f"{test_name}: {'✓' if result else '✗'}")
        
        return overall_success
    
    finally:
        # Clean up test environment
        if test_file_path:
            cleanup_test_environment(test_file_path)

class MockTaskInstance:
    """Mock Task Instance for testing."""
    def __init__(self):
        self.xcom_data = {}
    
    def xcom_push(self, key, value):
        self.xcom_data[key] = value
    
    def xcom_pull(self, task_ids, key):
        return self.xcom_data.get(key, [])


class MockDAG:
    """Mock DAG for testing."""
    def __init__(self):
        self.dag_id = "test_medical_data_dag"
        self.default_args = {"owner": "test"}

if __name__ == "__main__":
    logger.info("=== Starting Medical Data Pipeline Test ===")
    
    success = run_all_tests()
    
    if success:
        logger.info("All pipeline tests passed successfully")
        sys.exit(0)
    else:
        logger.error("Some pipeline tests failed")
        sys.exit(1)
