import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.pipeline.ingestion_pipeline import MedicalDataIngestionPipeline
from src.extraction.text_extractor import TextExtractor

class TestIngestionPipeline(unittest.TestCase):
    """Test suite for the medical data ingestion pipeline."""

    def setUp(self):
        """Set up test environment."""
        # Create a temp directory for processed files
        self.test_dir = Path(tempfile.mkdtemp())
        self.processed_dir = self.test_dir / "processed_data"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Create input directories
        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir(exist_ok=True)
        
        # Create more specific input directories
        (self.input_dir / "text_documents").mkdir(exist_ok=True)
        (self.input_dir / "pdf_documents").mkdir(exist_ok=True)
        (self.input_dir / "html_documents").mkdir(exist_ok=True)
        
        # Create a sample text file
        self.test_file = self.input_dir / "text_documents" / "test_medical_record.txt"
        with open(self.test_file, "w") as f:
            f.write("""
Patient Medical Record
Date: 2023-06-10
Provider: Dr. Alice Johnson

Assessment:
Patient presents with symptoms consistent with hypermobile EDS. Beighton score of 7/9.

Plan:
1. Physical therapy referral
2. Follow-up in 3 months
            """)

    def test_pipeline_initialization(self):
        """Test that the pipeline can be initialized with various configurations."""
        # Test with default configuration
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=False
        )
        self.assertIsNotNone(pipeline)
        
        # Test with AI models enabled
        pipeline_with_ai = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=True,
            store_in_db=False
        )
        self.assertIsNotNone(pipeline_with_ai)
        self.assertTrue(pipeline_with_ai.use_models)
        
        # Test with database storage enabled
        pipeline_with_db = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=True
        )
        self.assertIsNotNone(pipeline_with_db)
        self.assertTrue(pipeline_with_db.store_in_db)

    def test_process_file(self):
        """Test processing a single file through the pipeline."""
        # Initialize pipeline with minimal configuration
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=False
        )
        
        # Process the test file
        result = pipeline.process_file(str(self.test_file))
        
        # Verify result structure
        self.assertIsNotNone(result)
        self.assertIn("metadata", result)
        self.assertIn("content", result)
        
        # Check metadata
        metadata = result["metadata"]
        self.assertIn("file_path", metadata)
        self.assertEqual(str(self.test_file), metadata["file_path"])
        
        # Check content
        content = result["content"]
        self.assertIn("hypermobile EDS", content)
        self.assertIn("Beighton score", content)

    @patch("src.extraction.text_extractor.TextExtractor.process_file")
    def test_extractor_error_handling(self, mock_process_file):
        """Test that the pipeline handles extractor errors gracefully."""
        # Configure the mock to raise an exception
        mock_process_file.side_effect = Exception("Extraction error")
        
        # Initialize pipeline
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=False
        )
        
        # Process the file, expect it to handle the error
        result = pipeline.process_file(str(self.test_file))
        
        # Verify error was captured
        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertIn("Extraction error", result["error"])

    def test_process_directory(self):
        """Test processing a directory of files."""
        # Create additional test files
        test_file2 = self.input_dir / "text_documents" / "test_record2.txt"
        with open(test_file2, "w") as f:
            f.write("Another test medical record with POTS diagnosis.")
        
        # Initialize pipeline
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=False
        )
        
        # Process the directory
        results = pipeline.process_directory(str(self.input_dir / "text_documents"))
        
        # Verify results
        self.assertIsNotNone(results)
        self.assertEqual(2, len(results))
        
        # Verify file registry was created
        registry_file = self.processed_dir / "file_registry" / "processed_files.json"
        self.assertTrue(registry_file.exists())

    def test_post_processor_integration(self):
        """Test that post-processors are correctly integrated and called."""
        # Create a mock post-processor
        mock_post_processor = MagicMock()
        mock_post_processor.process.return_value = {"post_processed": True}
        
        # Initialize pipeline with the mock post-processor
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=False
        )
        
        # Register the mock post-processor
        pipeline.register_post_processor(mock_post_processor)
        
        # Process a file
        result = pipeline.process_file(str(self.test_file))
        
        # Verify post-processor was called
        mock_post_processor.process.assert_called_once()
        
        # Verify post-processing result was integrated
        self.assertIn("post_processed", result)
        self.assertTrue(result["post_processed"])

    def test_file_registry(self):
        """Test that the file registry correctly tracks processed files."""
        # Initialize pipeline
        pipeline = MedicalDataIngestionPipeline(
            processed_dir=str(self.processed_dir),
            use_models=False,
            store_in_db=False
        )
        
        # Process the test file
        pipeline.process_file(str(self.test_file))
        
        # Verify file was registered
        registry_file = self.processed_dir / "file_registry" / "processed_files.json"
        self.assertTrue(registry_file.exists())
        
        # Load the registry
        import json
        with open(registry_file, "r") as f:
            registry = json.load(f)
        
        # Verify the test file is in the registry
        self.assertIn(str(self.test_file), registry)
        
        # Check registry entry data
        entry = registry[str(self.test_file)]
        self.assertIn("timestamp", entry)
        self.assertIn("status", entry)
        self.assertEqual("success", entry["status"])

    def tearDown(self):
        """Clean up test environment."""
        # Remove temp directory and all contents
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    unittest.main() 