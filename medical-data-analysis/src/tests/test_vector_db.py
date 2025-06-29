import sys
import os
import json
import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.ai.vectordb.medical_vector_store import MedicalVectorStore
from src.ai.vectordb.pipeline_integration import VectorDBIntegration

class MockEmbeddingModel:
    """A mock embedding model for testing."""
    
    def __init__(self):
        """Initialize a mock embedding model."""
        self.dimension = 128
    
    def generate_embedding(self, text):
        """Generate a deterministic embedding based on input text."""
        np.random.seed(hash(text) % 2**32)
        return np.random.rand(self.dimension)

class TestVectorDBFunctionality(unittest.TestCase):
    """Test suite for vector database functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temp directory for vector database
        self.temp_dir = Path(tempfile.mkdtemp())
        self.vector_db_path = self.temp_dir / "vectordb"
        self.vector_db_path.mkdir(exist_ok=True)
        
        # Create a mock embedding model
        self.mock_model = MockEmbeddingModel()
        
        # Initialize the vector store with the mock model
        self.vector_store = MedicalVectorStore(
            storage_path=str(self.vector_db_path),
            use_gpu=False
        )
        
        # Save the original generate_embedding method for restoration
        self.original_generate_embedding = self.vector_store.generate_embedding
        
        # Override the generate_embedding method with our mock
        self.vector_store.generate_embedding = self.mock_model.generate_embedding

    def test_vector_store_initialization(self):
        """Test that the vector store can be initialized."""
        self.assertIsNotNone(self.vector_store)
        self.assertEqual(str(self.vector_db_path), self.vector_store.storage_path)
        self.assertFalse(self.vector_store.use_gpu)

    def test_document_storage_and_retrieval(self):
        """Test storing and retrieving documents in the vector store."""
        # Store a document
        doc_id = self.vector_store.store_document(
            text="Patient diagnosed with Ehlers-Danlos Syndrome with joint hypermobility.",
            metadata={"source": "test_document", "date": "2023-05-15"}
        )
        
        # Verify document was stored
        self.assertIsNotNone(doc_id)
        
        # Search for the document
        results = self.vector_store.search("Ehlers-Danlos", limit=1)
        
        # Verify a result was found
        self.assertEqual(1, len(results))
        self.assertEqual(doc_id, results[0]["id"])
        
        # Verify metadata was preserved
        self.assertEqual("test_document", results[0]["metadata"]["source"])
        self.assertEqual("2023-05-15", results[0]["metadata"]["date"])

    def test_entity_storage_and_retrieval(self):
        """Test storing and retrieving medical entities."""
        # Create a medical entity
        entity = {
            "type": "condition",
            "text": "hypermobile Ehlers-Danlos Syndrome",
            "start": 0,
            "end": 32,
            "metadata": {
                "certainty": "confirmed",
                "body_part": "systemic"
            }
        }
        
        # Store the entity
        entity_id = self.vector_store.store_entity(entity)
        
        # Verify entity was stored
        self.assertIsNotNone(entity_id)
        
        # Search for the entity
        results = self.vector_store.search("Ehlers-Danlos", entity_types=["condition"], limit=1)
        
        # Verify a result was found
        self.assertEqual(1, len(results))
        self.assertEqual(entity_id, results[0]["id"])
        self.assertEqual("condition", results[0]["entity_type"])
        
        # Verify metadata was preserved
        self.assertEqual("confirmed", results[0]["metadata"]["certainty"])
        self.assertEqual("systemic", results[0]["metadata"]["body_part"])

    def test_pipeline_integration(self):
        """Test the vector database pipeline integration."""
        # Create a VectorDBIntegration instance
        integration = VectorDBIntegration(
            vector_store=self.vector_store
        )
        
        # Create a sample processing result
        result = {
            "content": "Patient diagnosed with Ehlers-Danlos Syndrome with joint hypermobility.",
            "metadata": {
                "source": "test_document",
                "date": "2023-05-15"
            },
            "ai_analysis": {
                "entities": [
                    {
                        "type": "condition",
                        "text": "Ehlers-Danlos Syndrome",
                        "start": 23,
                        "end": 45,
                        "metadata": {
                            "certainty": "confirmed"
                        }
                    },
                    {
                        "type": "symptom",
                        "text": "joint hypermobility",
                        "start": 51,
                        "end": 70,
                        "metadata": {
                            "body_part": "joints"
                        }
                    }
                ]
            }
        }
        
        # Process the result with the integration
        processed_result = integration.process(result)
        
        # Verify the integration added vector DB information
        self.assertIn("vector_db", processed_result)
        self.assertIn("document_vector_id", processed_result["vector_db"])
        self.assertIn("entity_vector_ids", processed_result["vector_db"])
        
        # Check entity vector IDs
        entity_ids = processed_result["vector_db"]["entity_vector_ids"]
        self.assertEqual(2, len(entity_ids))
        self.assertIn("conditions", entity_ids)
        self.assertIn("symptoms", entity_ids)

    def test_numpy_json_serialization(self):
        """Test JSON serialization of numpy arrays."""
        from src.ai.vectordb.numpy_json import NumpyEncoder
        
        # Create a test object with numpy arrays
        test_obj = {
            "embedding": np.random.rand(10),
            "metadata": {
                "nested_array": np.array([1, 2, 3])
            }
        }
        
        # Serialize to JSON
        json_str = json.dumps(test_obj, cls=NumpyEncoder)
        
        # Deserialize
        deserialized = json.loads(json_str)
        
        # Verify arrays were properly serialized
        self.assertIsInstance(deserialized["embedding"], list)
        self.assertEqual(10, len(deserialized["embedding"]))
        self.assertIsInstance(deserialized["metadata"]["nested_array"], list)
        self.assertEqual([1, 2, 3], deserialized["metadata"]["nested_array"])

    def test_cleanup(self):
        """Test cleaning up the vector store."""
        # First, add some data to clean up
        self.vector_store.store_document(
            text="Test document for cleanup",
            metadata={"source": "cleanup_test"}
        )
        
        # Clean up
        self.vector_store.cleanup()
        
        # Verify storage is empty
        results = self.vector_store.search("cleanup", limit=10)
        self.assertEqual(0, len(results))

    def tearDown(self):
        """Clean up test environment."""
        # Restore original method
        if hasattr(self, 'original_generate_embedding'):
            self.vector_store.generate_embedding = self.original_generate_embedding
        
        # Close vector store
        self.vector_store.close()
        
        # Remove temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

if __name__ == "__main__":
    unittest.main() 