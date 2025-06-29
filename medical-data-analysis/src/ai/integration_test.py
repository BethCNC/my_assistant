"""
Integration test for the medical AI components.
Tests the full functionality of the AI pipeline on sample data.
"""

import logging
import os
import sys
import unittest
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import AI components
from src.ai.model_integration import MedicalAIIntegration
from src.ai.entity_extraction import MedicalEntityExtractor
from src.ai.text_analysis import MedicalTextAnalyzer
from src.ai.embedding import MedicalEmbedding
from src.ai.vector_storage import MedicalVectorStore
from src.ai.entity_standardization import standardize_entities

# Import database components
from src.database.models.entity import Document, Patient, HealthcareProvider

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class IntegrationTest(unittest.TestCase):
    """Integration test for the AI components."""
    
    def setUp(self):
        """Set up the test case."""
        # Determine if we should use a real DB session or a mock
        try:
            # Try to import and use a real session
            from src.database.connection import get_db_session
            self.db_session_maker = get_db_session
            self.real_db_session = get_db_session()
            self.db_session = self.real_db_session.__enter__()
            self.using_real_db = True
        except Exception as e:
            # Use a mock session if can't connect to real DB
            logger.warning(f"Couldn't connect to real database: {e}. Using mock session.")
            self.db_session = MockSession()
            self.using_real_db = False
        
        # Create test data
        self._create_test_data()
        
        # Initialize the AI components
        self.entity_extractor = MedicalEntityExtractor()
        self.text_analyzer = MedicalTextAnalyzer()
        self.embedding_model = MedicalEmbedding()
        self.vector_store = MedicalVectorStore()
        
        # Initialize the AI integration
        self.ai_integration = MedicalAIIntegration(self.db_session)
    
    def tearDown(self):
        """Tear down the test case."""
        # Clean up database session if using real DB
        if self.using_real_db:
            try:
                self.db_session.rollback()
                self.real_db_session.__exit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error during tearDown: {e}")
    
    def _create_test_data(self):
        """Create test data for integration tests."""
        # Create a patient for testing
        self.patient = Patient(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1980, 1, 15),
            gender="Male",
            has_eds=True,
            eds_type="Hypermobility",
            has_neurodivergence=True,
            neurodivergence_type="ADHD"
        )
        
        # Create a healthcare provider for testing
        self.provider = HealthcareProvider(
            name="Dr. Jane Smith",
            specialty="Rheumatology",
            facility="General Hospital"
        )
        
        # Create a document for testing
        self.document = Document(
            patient_id=self.patient.id,
            provider_id=self.provider.id,
            document_type="clinical_note",
            document_date=datetime(2023, 5, 15),
            content="Patient presents with joint pain and fatigue. History of EDS hypermobility type. " +
                    "Currently taking ibuprofen 400mg twice daily for pain management. " +
                    "Lab results show normal inflammatory markers. Recommend physical therapy.",
            source="General Hospital"
        )
        
        # Commit changes
        self.db_session.add(self.patient)
        self.db_session.add(self.provider)
        self.db_session.add(self.document)
        self.db_session.commit()
    
    def test_process_document(self):
        """Test document processing."""
        # Process the document text directly
        document_text = str(self.document.content)
        document_type = str(self.document.document_type)
        document_date = datetime(2023, 5, 15)
        document_metadata = {"facility": "Test Hospital", "provider": "Dr. Smith"}
        patient_id = "1"
        
        # Process the document
        result = self.ai_integration.process_document(
            document_text=document_text,
            document_type=document_type,
            document_date=document_date,
            document_metadata=document_metadata,
            patient_id=patient_id
        )
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIn('document_id', result)
    
    def test_analyze_patient_history(self):
        """Test patient history analysis."""
        # Analyze patient history
        patient_id = str(self.patient.id) if hasattr(self.patient, 'id') else "1"
        result = self.ai_integration.analyze_patient_history(patient_id)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIn('conditions', result)
        self.assertIn('symptoms', result)
    
    def test_answer_medical_question(self):
        """Test medical question answering."""
        # Answer a medical question
        question = "What are the symptoms of EDS?"
        patient_id = str(self.patient.id) if hasattr(self.patient, 'id') else "1"
        result = self.ai_integration.answer_medical_question(patient_id, question)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIn('answer', result)
    
    def test_extract_medical_timeline(self):
        """Test medical timeline extraction."""
        # Extract medical timeline
        patient_id = str(self.patient.id) if hasattr(self.patient, 'id') else "1"
        result = self.ai_integration.extract_medical_timeline(patient_id)
        
        # Check result
        self.assertIsNotNone(result)
        self.assertIn('timeline', result)

if __name__ == '__main__':
    unittest.main() 