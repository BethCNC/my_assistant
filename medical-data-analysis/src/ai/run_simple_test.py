#!/usr/bin/env python3
"""
Simple test script for AI integration.

This script tests the AI integration without relying on database operations.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the AI components
from src.ai.model_integration import MedicalAIIntegration
from src.ai.entity_extraction import MedicalEntityExtractor
from src.ai.text_analysis import MedicalTextAnalyzer
from src.ai.embedding import MedicalEmbedding
from src.ai.vector_storage import MedicalVectorStore

class MockSession:
    """Mock database session for testing."""
    def __init__(self):
        self.added = []
        self.queries = {}
        
    def add(self, obj):
        """Mock adding an object to the session."""
        self.added.append(obj)
        
    def commit(self):
        """Mock committing the session."""
        pass
        
    def flush(self):
        """Mock flushing the session."""
        pass
    
    def rollback(self):
        """Mock rolling back the session."""
        pass
        
    def close(self):
        """Mock closing the session."""
        pass
    
    def query(self, cls):
        """Mock querying the session."""
        return MockQuery(self, cls)

class MockQuery:
    """Mock query for testing."""
    def __init__(self, session, cls):
        self.session = session
        self.cls = cls
        self.filters = []
        
    def filter(self, *args):
        """Mock filter."""
        return self
        
    def filter_by(self, **kwargs):
        """Mock filter_by."""
        return self
        
    def first(self):
        """Mock first."""
        return None
        
    def all(self):
        """Mock all."""
        return []

def test_process_document():
    """Test processing a document."""
    # Create a mock session
    mock_session = MockSession()
    
    # Create the AI integration
    ai = MedicalAIIntegration(mock_session)
    
    # Test document processing with all required parameters
    document_text = 'Patient presents with joint hypermobility and chronic pain.'
    document_type = 'clinical_note'
    document_date = datetime.now()
    document_metadata = {
        'facility': 'General Hospital'
    }
    patient_id = '67890'
    
    result = ai.process_document(
        document_text=document_text,
        document_type=document_type,
        document_date=document_date,
        document_metadata=document_metadata,
        patient_id=patient_id
    )
    logger.info(f"Document processing result: {result}")
    
    # Should have a document ID
    assert result is not None, "Expected non-None result"
    assert 'document_id' in result, f"Expected 'document_id' in result, got {result}"
    
    return "Document processing test: PASSED"

def test_analyze_patient_history():
    """Test analyzing patient history."""
    # Create a mock session
    mock_session = MockSession()
    
    # Create the AI integration
    ai = MedicalAIIntegration(mock_session)
    
    # Test patient history analysis
    result = ai.analyze_patient_history('67890')
    logger.info(f"Patient history analysis result: {result}")
    
    # Should have some mock data
    assert result is not None, "Expected non-None result"
    
    return "Patient history analysis test: PASSED"

def test_answer_medical_question():
    """Test answering a medical question."""
    # Create a mock session
    mock_session = MockSession()
    
    # Create the AI integration
    ai = MedicalAIIntegration(mock_session)
    
    # Test question answering
    result = ai.answer_medical_question('67890', "What are common symptoms of EDS?")
    logger.info(f"Question answering result: {result}")
    
    # Should have some mock data
    assert result is not None, "Expected non-None result"
    assert 'answer' in result, "Expected 'answer' in result"
    
    return "Question answering test: PASSED"

def test_extract_medical_timeline():
    """Test extracting a medical timeline."""
    # Create a mock session
    mock_session = MockSession()
    
    # Create the AI integration
    ai = MedicalAIIntegration(mock_session)
    
    # Test timeline extraction
    result = ai.extract_medical_timeline('67890')
    logger.info(f"Timeline extraction result: {result}")
    
    # Should have some mock data
    assert result is not None, "Expected non-None result"
    assert 'timeline' in result, "Expected 'timeline' in result"
    
    return "Timeline extraction test: PASSED"

def test_text_analysis():
    """Test text analysis."""
    # Create the text analyzer
    analyzer = MedicalTextAnalyzer()
    
    # Test text analysis
    text = "Patient has a history of joint hypermobility and chronic pain."
    result = analyzer.analyze_text(text)
    logger.info(f"Text analysis result: {result}")
    
    # Should have some data
    assert result is not None, "Expected non-None result"
    
    return "Text analysis test: PASSED"

def test_entity_extraction():
    """Test entity extraction."""
    # Create the entity extractor
    extractor = MedicalEntityExtractor()
    
    # Test entity extraction
    text = "Patient has been diagnosed with EDS and is taking ibuprofen for pain."
    result = extractor.extract_entities(text)
    logger.info(f"Entity extraction result: {result}")
    
    # Should have some data
    assert result is not None, "Expected non-None result"
    assert 'conditions' in result, "Expected 'conditions' in result"
    assert 'medications' in result, "Expected 'medications' in result"
    
    return "Entity extraction test: PASSED"

def test_embedding():
    """Test embedding generation."""
    # Create the embedding model
    embedding_model = MedicalEmbedding()
    
    # Test embedding generation
    text = "Ehlers-Danlos Syndrome is a group of connective tissue disorders."
    result = embedding_model.generate_embedding(text)
    logger.info(f"Embedding shape: {result.shape}")
    
    # Should have the correct shape
    assert result is not None, "Expected non-None result"
    assert len(result.shape) == 1, "Expected 1D array"
    assert result.shape[0] == embedding_model.dimension, f"Expected dimension {embedding_model.dimension}"
    
    return "Embedding test: PASSED"

def test_vector_storage():
    """Test vector storage."""
    # Create the vector store
    vector_store = MedicalVectorStore(storage_dir="./test_vector_data")
    
    # Create an embedding
    embedding_model = MedicalEmbedding()
    text = "Ehlers-Danlos Syndrome is a group of connective tissue disorders."
    embedding = embedding_model.generate_embedding(text)
    
    # Store the embedding
    vector_store.add_entity("eds_description", embedding, {"text": text})
    
    # Search for similar embeddings
    query_embedding = embedding_model.generate_embedding("connective tissue disorders")
    results = vector_store.search_similar(query_embedding, top_k=1)
    logger.info(f"Vector search results: {results}")
    
    # Should have some results
    assert results is not None, "Expected non-None results"
    assert len(results) > 0, "Expected at least one result"
    
    # Clean up
    import os
    import shutil
    if os.path.exists("./test_vector_data"):
        shutil.rmtree("./test_vector_data")
    
    return "Vector storage test: PASSED"

def main():
    """Run all tests."""
    try:
        print("\n---- TESTING AI COMPONENTS ----\n")
        
        # Run all tests
        print(test_process_document())
        print(test_analyze_patient_history())
        print(test_answer_medical_question())
        print(test_extract_medical_timeline())
        print(test_text_analysis())
        print(test_entity_extraction())
        print(test_embedding())
        print(test_vector_storage())
        
        print("\nAll tests PASSED!")
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        print(f"\nTEST FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 