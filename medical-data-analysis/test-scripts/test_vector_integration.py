#!/usr/bin/env python3
"""
Test Vector Database Integration with the Medical Data Pipeline

This script tests whether the vector database can be properly integrated
with the medical data processing pipeline.
"""

import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to test vector database integration with pipeline."""
    logger.info("=== Testing Vector Database and Pipeline Integration ===")
    
    # Create directories
    os.makedirs("vectordb", exist_ok=True)
    os.makedirs("processed_data", exist_ok=True)
    
    # Import pipeline components
    try:
        from src.pipeline.ingestion_pipeline import IngestionPipeline
        from src.ai.vectordb.pipeline_integration import VectorDBPostProcessor
        
        # Create the pipeline
        pipeline = IngestionPipeline(
            input_dir="input",
            processed_dir="processed_data"
        )
        logger.info("✓ Pipeline created successfully")
        
        # Create the vector database post-processor
        post_processor = VectorDBPostProcessor(
            vector_db_path="vectordb",
            use_gpu=False
        )
        logger.info("✓ Vector DB post-processor created successfully")
        
        # Register the post-processor with the pipeline
        pipeline.register_post_processor(post_processor.process)
        logger.info("✓ Post-processor registered with pipeline")
        
        # Create a sample document for testing
        test_doc = {
            "id": "test-document-001",
            "content": "Patient has been diagnosed with hypermobile Ehlers-Danlos Syndrome (hEDS) with joint hypermobility and chronic pain.",
            "metadata": {
                "source": "test",
                "file_path": "test_document.txt",
                "extraction_date": "2025-04-30"
            },
            "document_type": "test_document"
        }
        
        # Process the document
        logger.info("Processing test document...")
        result = post_processor.process(test_doc)
        
        # Verify results
        if "vector_db" in result and "document_vector_id" in result["vector_db"]:
            logger.info(f"✓ Document added to vector database successfully with ID: {result['vector_db']['document_vector_id']}")
            
            # Search for similar documents
            try:
                from src.ai.vectordb.medical_vector_store import MedicalVectorStore
                
                vector_store = MedicalVectorStore(storage_path="vectordb")
                search_results = vector_store.search(query_text="Ehlers-Danlos Syndrome", limit=1)
                
                if search_results:
                    logger.info(f"✓ Found similar document with similarity score: {search_results[0]['similarity']}")
                else:
                    logger.error("✗ No similar documents found")
                    return False
                
            except Exception as e:
                logger.error(f"✗ Error searching vector database: {e}")
                return False
                
            logger.info("✓ Vector database integration test PASSED")
            return True
        else:
            logger.error("✗ Document was not added to vector database")
            logger.error(f"Result: {result}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during integration test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("=== Vector Database Integration Test PASSED ===")
        exit(0)
    else:
        logger.error("=== Vector Database Integration Test FAILED ===")
        exit(1) 