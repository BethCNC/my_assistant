#!/usr/bin/env python3
"""
Vector Database Validation Script

This script checks if the vector database is properly set up and functioning.
It's a simplified version of the full pipeline test focused only on vector storage.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_imports():
    """Check if all required modules can be imported."""
    missing_modules = []
    
    # Check core modules
    try:
        from src.ai.vectordb.medical_vector_store import MedicalVectorStore
        logger.info("✓ MedicalVectorStore module can be imported")
    except ImportError as e:
        logger.error(f"✗ Failed to import MedicalVectorStore: {e}")
        missing_modules.append("MedicalVectorStore")
    
    try:
        from src.ai.vectordb.pipeline_integration import create_vector_db_integration
        logger.info("✓ Vector DB integration module can be imported")
    except ImportError as e:
        logger.error(f"✗ Failed to import vector DB integration: {e}")
        missing_modules.append("pipeline_integration")
    
    # Check pipeline module
    try:
        from src.pipeline.ingestion_pipeline import IngestionPipeline
        logger.info("✓ Pipeline module can be imported")
    except ImportError as e:
        logger.error(f"✗ Failed to import pipeline module: {e}")
        missing_modules.append("ingestion_pipeline")
    
    return len(missing_modules) == 0

def check_vector_db():
    """Check if vector database components are working."""
    logger.info("Starting vector database check...")
    
    # Check for required directory
    vector_db_path = Path("vectordb")
    if not vector_db_path.exists():
        logger.info("Creating vector database directory")
        os.makedirs("vectordb", exist_ok=True)
    
    # Check if we can initialize the vector store
    try:
        from src.ai.vectordb.medical_vector_store import MedicalVectorStore
        
        vector_store = MedicalVectorStore(
            storage_path="vectordb",
            embedding_model="pritamdeka/S-PubMedBert-MS-MARCO",
            use_gpu=False
        )
        logger.info("✓ Successfully initialized vector store")
        
        # Check if we can add and query vectors
        test_text = "This is a test medical document about hypermobility and chronic pain."
        test_id = "test-doc-001"
        
        # Add a test document
        vector_id = vector_store.add_document(
            document_id=test_id,
            text=test_text,
            metadata={"source": "test", "type": "medical_note"}
        )
        logger.info(f"✓ Successfully added test document to vector store with ID: {vector_id}")
        
        # Query the vector store
        results = vector_store.search(
            query_text="hypermobility symptoms",
            limit=1
        )
        
        if results and len(results) > 0:
            logger.info("✓ Successfully queried vector store")
        else:
            logger.error("✗ Failed to retrieve results from vector store")
            return False
        
        # Check integration with pipeline
        try:
            from src.ai.vectordb.pipeline_integration import create_vector_db_integration
            from src.pipeline.ingestion_pipeline import IngestionPipeline
            
            # Create a minimal pipeline for testing
            try:
                pipeline = IngestionPipeline(
                    input_dir=None,
                    output_dir=None,
                    processed_dir="processed_data",
                    models_dir=None,
                    session=None,
                    use_gpu=False
                )
                logger.info("✓ Successfully created test pipeline")
            except Exception as e:
                logger.error(f"✗ Failed to create test pipeline: {e}")
                return False
            
            # Create vector DB integration
            try:
                integration = create_vector_db_integration(
                    pipeline=pipeline,
                    vector_db_path="vectordb",
                    use_gpu=False
                )
                logger.info("✓ Successfully created vector DB integration")
            except Exception as e:
                logger.error(f"✗ Failed to create vector DB integration: {e}")
                return False
            
            logger.info("✓ Vector database integration check passed")
            
        except Exception as e:
            logger.error(f"✗ Error during integration check: {e}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"✗ Error during vector database check: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Starting Vector Database Validation ===")
    
    # Check imports
    if not check_imports():
        logger.error("✗ Import check failed. Fixing module imports is required.")
        sys.exit(1)
    
    # Check vector DB functionality
    if check_vector_db():
        logger.info("✓ Vector database check PASSED")
        sys.exit(0)
    else:
        logger.error("✗ Vector database check FAILED")
        sys.exit(1) 