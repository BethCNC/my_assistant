import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.ai.model_integration import MedicalEntityExtractor, ModelIntegration
from src.ai.entity_standardization import standardize_medical_entity

class MockModel:
    """Mock NLP model for testing."""
    
    def __init__(self):
        """Initialize the mock model."""
        pass
    
    def __call__(self, text):
        """Process text and return mock entities."""
        # Return predefined entities based on recognized keywords
        entities = []
        
        # Check for conditions
        if "EDS" in text or "Ehlers-Danlos" in text:
            entities.append({
                "entity": "CONDITION",
                "start": text.find("EDS") if "EDS" in text else text.find("Ehlers-Danlos"),
                "end": text.find("EDS") + 3 if "EDS" in text else text.find("Ehlers-Danlos") + 13,
                "text": "EDS" if "EDS" in text else "Ehlers-Danlos"
            })
        
        if "POTS" in text:
            entities.append({
                "entity": "CONDITION",
                "start": text.find("POTS"),
                "end": text.find("POTS") + 4,
                "text": "POTS"
            })
        
        # Check for symptoms
        if "hypermobility" in text or "hypermobile" in text:
            keyword = "hypermobility" if "hypermobility" in text else "hypermobile"
            entities.append({
                "entity": "SYMPTOM",
                "start": text.find(keyword),
                "end": text.find(keyword) + len(keyword),
                "text": keyword
            })
        
        if "joint pain" in text:
            entities.append({
                "entity": "SYMPTOM",
                "start": text.find("joint pain"),
                "end": text.find("joint pain") + 10,
                "text": "joint pain"
            })
        
        # Check for treatments
        if "physical therapy" in text:
            entities.append({
                "entity": "TREATMENT",
                "start": text.find("physical therapy"),
                "end": text.find("physical therapy") + 16,
                "text": "physical therapy"
            })
        
        return {"entities": entities}

class TestAIProcessing(unittest.TestCase):
    """Test suite for AI processing and entity extraction."""

    def setUp(self):
        """Set up test environment."""
        # Sample medical text for testing
        self.test_text = """
        Patient diagnosed with hypermobile Ehlers-Danlos Syndrome (hEDS) in 2020.
        Reports chronic joint pain and fatigue. Currently receiving physical therapy.
        Follow-up evaluation for POTS scheduled for next month.
        """
        
        # Create a patcher for the NLP model loading
        self.model_patcher = patch('src.ai.model_integration.load_nlp_model')
        self.mock_load_model = self.model_patcher.start()
        
        # Set the mock model as the return value
        self.mock_load_model.return_value = MockModel()

    def test_entity_extractor_initialization(self):
        """Test that the entity extractor can be initialized."""
        extractor = MedicalEntityExtractor()
        self.assertIsNotNone(extractor)
        self.mock_load_model.assert_called_once()

    def test_entity_extraction(self):
        """Test extracting medical entities from text."""
        extractor = MedicalEntityExtractor()
        
        # Extract entities
        entities = extractor.extract_entities(self.test_text)
        
        # Verify entities were extracted
        self.assertIsNotNone(entities)
        self.assertGreater(len(entities), 0)
        
        # Check entity types
        entity_types = set(entity["type"] for entity in entities)
        self.assertIn("condition", entity_types)
        self.assertIn("symptom", entity_types)
        self.assertIn("treatment", entity_types)
        
        # Verify specific entities
        condition_entities = [e for e in entities if e["type"] == "condition"]
        symptom_entities = [e for e in entities if e["type"] == "symptom"]
        treatment_entities = [e for e in entities if e["type"] == "treatment"]
        
        # Check conditions
        self.assertEqual(2, len(condition_entities))
        condition_texts = [e["text"] for e in condition_entities]
        self.assertTrue("EDS" in condition_texts or "Ehlers-Danlos" in condition_texts)
        self.assertIn("POTS", condition_texts)
        
        # Check symptoms
        self.assertGreaterEqual(len(symptom_entities), 1)
        symptom_texts = [e["text"] for e in symptom_entities]
        self.assertTrue("hypermobility" in symptom_texts or "hypermobile" in symptom_texts)
        
        # Check treatments
        self.assertEqual(1, len(treatment_entities))
        self.assertEqual("physical therapy", treatment_entities[0]["text"])

    def test_entity_standardization(self):
        """Test standardization of medical entities."""
        # Create test entities
        test_entities = [
            {
                "type": "condition",
                "text": "EDS",
                "start": 0,
                "end": 3
            },
            {
                "type": "condition",
                "text": "Ehlers-Danlos Syndrome",
                "start": 5,
                "end": 27
            },
            {
                "type": "condition",
                "text": "POTS",
                "start": 30,
                "end": 34
            }
        ]
        
        # Standardize entities
        standardized = [standardize_medical_entity(entity) for entity in test_entities]
        
        # Verify standardization
        self.assertEqual("Ehlers-Danlos Syndrome", standardized[0]["standard_name"])
        self.assertEqual("Ehlers-Danlos Syndrome", standardized[1]["standard_name"])
        self.assertEqual("Postural Orthostatic Tachycardia Syndrome", standardized[2]["standard_name"])
        
        # Check that original text is preserved
        self.assertEqual("EDS", standardized[0]["text"])
        self.assertEqual("Ehlers-Danlos Syndrome", standardized[1]["text"])
        self.assertEqual("POTS", standardized[2]["text"])
        
        # Check that ICD-10 codes are added where available
        self.assertIn("icd10", standardized[0])
        self.assertIn("icd10", standardized[1])
        self.assertIn("icd10", standardized[2])

    def test_model_integration(self):
        """Test the complete model integration pipeline."""
        # Create a model integration instance
        integration = ModelIntegration()
        
        # Process a sample result
        sample_result = {
            "content": self.test_text,
            "metadata": {
                "file_path": "/path/to/sample.txt",
                "date": "2023-06-15"
            }
        }
        
        # Process with model integration
        processed_result = integration.process(sample_result)
        
        # Verify AI analysis was added
        self.assertIn("ai_analysis", processed_result)
        
        # Check entity extraction
        self.assertIn("entities", processed_result["ai_analysis"])
        entities = processed_result["ai_analysis"]["entities"]
        self.assertGreater(len(entities), 0)
        
        # Check entity types
        entity_types = set(entity["type"] for entity in entities)
        self.assertIn("condition", entity_types)
        self.assertIn("symptom", entity_types)
        
        # Verify all entities have standardized names
        for entity in entities:
            if entity["type"] == "condition":
                self.assertIn("standard_name", entity)

    def test_error_handling(self):
        """Test error handling in entity extraction."""
        # Configure model to raise an exception
        self.mock_load_model.return_value = MagicMock(side_effect=Exception("Model error"))
        
        # Create extractor, should handle the error
        extractor = MedicalEntityExtractor()
        
        # Extract entities, should return empty list
        entities = extractor.extract_entities(self.test_text)
        
        # Verify empty list is returned on error
        self.assertEqual(0, len(entities))

    def tearDown(self):
        """Clean up test environment."""
        # Stop the patcher
        self.model_patcher.stop()

if __name__ == "__main__":
    unittest.main() 