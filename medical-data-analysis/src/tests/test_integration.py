"""
Integration Tests for Medical Data Pipeline

Tests the complete flow of the medical data pipeline from file extraction
to database storage and AI analysis.
"""

import sys
import os
import unittest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.pipeline.ingestion_pipeline import MedicalDataIngestionPipeline
from src.ai.vectordb.pipeline_integration import VectorDBIntegration
from src.ai.model_integration import ModelIntegration
from src.tests.test_config import (
    setup_test_directory_structure,
    create_sample_medical_files,
    cleanup_test_dir,
    SAMPLE_MEDICAL_TEXTS
)


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the complete medical data pipeline."""

    def setUp(self):
        """Set up test environment with a complete directory structure."""
        # Create a temp directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Set up directory structure
        self.dirs = setup_test_directory_structure(self.test_dir)
        
        # Create sample files
        self.files = create_sample_medical_files(self.dirs)
        
        # Create db directory
        self.db_dir = self.test_dir / "db"
        self.db_dir.mkdir(exist_ok=True)
        
        # Create vector db directory
        self.vector_db_dir = self.test_dir / "vector_db"
        self.vector_db_dir.mkdir(exist_ok=True)
        
        # Create patchers for expensive or external operations
        self.db_patcher = patch('src.database.session.get_session')
        self.mock_get_session = self.db_patcher.start()
        self.mock_session = MagicMock()
        self.mock_get_session.return_value.__enter__.return_value = self.mock_session
        
        # Create mock embedding model
        self.embedding_patcher = patch('src.ai.vectordb.medical_vector_store.MedicalVectorStore.generate_embedding')
        self.mock_generate_embedding = self.embedding_patcher.start()
        self.mock_generate_embedding.return_value = [0.1] * 128  # Mock 128-dim embedding
        
        # Create mock NLP model
        self.nlp_patcher = patch('src.ai.model_integration.load_nlp_model')
        self.mock_load_nlp = self.nlp_patcher.start()
        self.mock_nlp_model = MagicMock()
        self.mock_nlp_model.return_value = {"entities": [
            {
                "entity": "CONDITION",
                "start": 10, 
                "end": 32,
                "text": "Ehlers-Danlos Syndrome"
            },
            {
                "entity": "SYMPTOM",
                "start": 50,
                "end": 60,
                "text": "joint pain"
            }
        ]}
        self.mock_load_nlp.return_value = self.mock_nlp_model

    def test_full_pipeline_integration(self):
        """Test the complete pipeline flow with all components."""
        # Initialize pipeline with all components enabled
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.dirs["output"]),
            use_models=True,
            store_in_db=True
        )
        
        # Register vector DB integration
        vector_db = VectorDBIntegration(
            vector_db_path=str(self.vector_db_dir)
        )
        pipeline.register_post_processor(vector_db)
        
        # Register model integration
        model_integration = ModelIntegration()
        pipeline.register_post_processor(model_integration)
        
        # Process the directory with EDS test file
        results = pipeline.process_file(str(self.files["eds_text"]))
        
        # Verify results
        self.assertIsNotNone(results)
        self.assertIn("metadata", results)
        self.assertIn("content", results)
        
        # Verify AI analysis was added
        self.assertIn("ai_analysis", results)
        
        # Verify entities were extracted
        self.assertIn("entities", results["ai_analysis"])
        
        # Check that database operations were called
        self.mock_session.add.assert_called()
        self.mock_session.commit.assert_called()
        
        # Verify embedding was generated
        self.mock_generate_embedding.assert_called()
        
        # Verify output files were created
        extracted_dir = self.dirs["output"] / "extracted"
        processed_dir = self.dirs["output"] / "processed"
        registry_dir = self.dirs["output"] / "file_registry"
        
        # Check that files were created in output directories
        extracted_files = list(extracted_dir.glob("*.json"))
        processed_files = list(processed_dir.glob("*.json"))
        registry_files = list(registry_dir.glob("*.json"))
        
        self.assertGreater(len(extracted_files), 0)
        self.assertGreater(len(processed_files), 0)
        self.assertGreater(len(registry_files), 0)
        
        # Verify registry file content
        registry_file = registry_dir / "processed_files.json"
        self.assertTrue(registry_file.exists())
        
        with open(registry_file, "r") as f:
            registry = json.load(f)
        
        self.assertIn(str(self.files["eds_text"]), registry)

    def test_pipeline_with_multiple_files(self):
        """Test processing multiple files through the pipeline."""
        # Initialize pipeline with minimal configuration
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.dirs["output"]),
            use_models=False,
            store_in_db=False
        )
        
        # Process the directory with all sample files
        results = pipeline.process_directory(str(self.dirs["text_input"]))
        
        # Verify results
        self.assertIsNotNone(results)
        self.assertEqual(3, len(results))  # Should process all 3 test files
        
        # Check that results contain data from all files
        result_texts = [r["content"] for r in results]
        self.assertTrue(any("Ehlers-Danlos" in text for text in result_texts))
        self.assertTrue(any("autism spectrum" in text for text in result_texts))
        self.assertTrue(any("POTS" in text for text in result_texts))
        
        # Verify registry file has all entries
        registry_file = self.dirs["output"] / "file_registry" / "processed_files.json"
        self.assertTrue(registry_file.exists())
        
        with open(registry_file, "r") as f:
            registry = json.load(f)
        
        self.assertEqual(3, len(registry))
        
        # Check all files are in registry
        self.assertIn(str(self.files["eds_text"]), registry)
        self.assertIn(str(self.files["asd_text"]), registry)
        self.assertIn(str(self.files["comorbid_text"]), registry)

    def test_error_handling_and_recovery(self):
        """Test that the pipeline can handle errors and continue processing."""
        # Configure the mock NLP model to raise an exception for one specific file
        original_call = self.mock_nlp_model.__call__
        
        def side_effect(text):
            if "autism" in text:
                raise Exception("Error processing autism text")
            return original_call(text)
        
        self.mock_nlp_model.side_effect = side_effect
        
        # Initialize pipeline with models enabled
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.dirs["output"]),
            use_models=True,
            store_in_db=False
        )
        
        # Register model integration
        model_integration = ModelIntegration()
        pipeline.register_post_processor(model_integration)
        
        # Process all files
        results = pipeline.process_directory(str(self.dirs["text_input"]))
        
        # Verify we still get results for all files
        self.assertEqual(3, len(results))
        
        # Check the registry
        registry_file = self.dirs["output"] / "file_registry" / "processed_files.json"
        with open(registry_file, "r") as f:
            registry = json.load(f)
        
        # Verify all files are in registry
        self.assertEqual(3, len(registry))
        
        # Check status of problematic file
        asd_file_path = str(self.files["asd_text"])
        self.assertIn(asd_file_path, registry)
        
        # The ASD file should have an error status
        asd_entry = registry[asd_file_path]
        self.assertIn("status", asd_entry)
        self.assertIn("error", asd_entry)

    def tearDown(self):
        """Clean up test environment."""
        # Stop patchers
        self.db_patcher.stop()
        self.embedding_patcher.stop()
        self.nlp_patcher.stop()
        
        # Remove temp directory and all contents
        cleanup_test_dir(self.test_dir)

if __name__ == "__main__":
    unittest.main() 