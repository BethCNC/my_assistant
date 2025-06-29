"""
Simple test script for AI integration.

This script tests the AI integration without relying on database operations.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the AI integration
from src.ai.model_integration import MedicalAIIntegration

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

def test_process_document():
    """Test processing a document."""
    # Create a mock session
    mock_session = MockSession()
    
    # Create the AI integration
    ai = MedicalAIIntegration(mock_session)
    
    # Import datetime for the document date
    from datetime import datetime
    
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
    
    # We don't assert on the timeline length since our mock session doesn't have a patient with this ID
    # so we get an empty timeline
    
    return "Timeline extraction test: PASSED"

def main():
    """Run all tests."""
    try:
        print("\n---- TESTING AI INTEGRATION ----\n")
        
        # Run all tests
        print(test_process_document())
        print(test_analyze_patient_history())
        print(test_answer_medical_question())
        print(test_extract_medical_timeline())
        
        print("\nAll tests PASSED!")
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        print(f"\nTEST FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 