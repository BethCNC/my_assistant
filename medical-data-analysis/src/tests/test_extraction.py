import sys
import os
import unittest
import tempfile
from pathlib import Path

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.extraction.factory import get_extractor
from src.extraction.text_extractor import TextExtractor
from src.extraction.pdf_extractor import PDFExtractor
from src.extraction.html_extractor import HTMLExtractor
from src.extraction.csv_extractor import CSVExtractor

class TestExtractionComponents(unittest.TestCase):
    """Test suite for document extraction components."""

    def setUp(self):
        """Set up test environment with sample files."""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create sample text file
        self.text_file = self.test_dir / "sample.txt"
        with open(self.text_file, "w") as f:
            f.write("Patient: Jane Doe\nDate: 2023-05-15\nDiagnosis: Hypermobility\n")
        
        # Create sample HTML file
        self.html_file = self.test_dir / "sample.html"
        with open(self.html_file, "w") as f:
            f.write("<html><body><h1>Medical Report</h1><p>Patient: John Smith</p></body></html>")
        
        # Create sample CSV file
        self.csv_file = self.test_dir / "sample.csv"
        with open(self.csv_file, "w") as f:
            f.write("Date,Symptom,Severity\n2023-05-15,Joint Pain,Moderate\n2023-05-16,Fatigue,Severe\n")

    def test_factory_extractor_selection(self):
        """Test that the factory selects the correct extractor for each file type."""
        # Test text extractor
        extractor = get_extractor(self.text_file)
        self.assertIsInstance(extractor, TextExtractor)
        
        # Test HTML extractor
        extractor = get_extractor(self.html_file)
        self.assertIsInstance(extractor, HTMLExtractor)
        
        # Test CSV extractor
        extractor = get_extractor(self.csv_file)
        self.assertIsInstance(extractor, CSVExtractor)
        
        # Test non-existent file
        non_existent_file = self.test_dir / "non_existent.txt"
        extractor = get_extractor(non_existent_file)
        self.assertIsNone(extractor)

    def test_text_extraction(self):
        """Test extraction from text files."""
        # Create a sample text file
        text_file = self.test_dir / "sample.txt"
        with open(text_file, "w") as f:
            f.write("Patient: Jane Doe\nDate: 2023-05-15\nDiagnosis: Hypermobility\n")
        
        # Create text extractor
        extractor = TextExtractor()
        
        # Process the file
        result = extractor.process_file(text_file)
        
        # Check results
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIn("Patient: Jane Doe", result["content"])
        self.assertIn("confidence_score", result)
        
    def test_html_extraction(self):
        """Test extraction from HTML files."""
        # Create a sample HTML file
        html_file = self.test_dir / "sample.html"
        with open(html_file, "w") as f:
            f.write("<html><body><h1>Medical Report</h1><p>Patient: John Smith</p></body></html>")
        
        # Create HTML extractor
        extractor = HTMLExtractor()
        
        # Process the file
        result = extractor.process_file(html_file)
        
        # Check results
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIn("Medical Report", result["content"])
        self.assertIn("confidence_score", result)
        
    def test_csv_extraction(self):
        """Test extraction from CSV files."""
        # Create a sample CSV file
        csv_file = self.test_dir / "sample.csv"
        with open(csv_file, "w") as f:
            f.write("Date,Symptom,Severity\n2023-05-15,Joint Pain,Moderate\n2023-05-16,Fatigue,Severe")
        
        # Create CSV extractor
        extractor = CSVExtractor()
        
        # Process the file
        result = extractor.process_file(csv_file)
        
        # Check results
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIn("Joint Pain", result["content"])
        self.assertIn("confidence_score", result)

    def tearDown(self):
        """Clean up test environment."""
        # Remove test files
        for file_path in [self.text_file, self.html_file, self.csv_file]:
            if file_path.exists():
                file_path.unlink()
        
        # Remove test directory
        self.test_dir.rmdir()

if __name__ == "__main__":
    unittest.main() 