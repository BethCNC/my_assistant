"""
Entity models for medical data.

Contains entity models for medical data such as patients, providers,
medical events, conditions, medications, and symptoms.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, ForeignKey, Table, Integer, Float, Boolean, DateTime, Enum, MetaData
from sqlalchemy.orm import relationship
import uuid

# Import the real SQLAlchemy Base
from src.database.connection import Base

# Forward declare association tables (they will be defined later)
event_condition_association = None
event_medication_association = None
event_symptom_association = None
event_provider_association = None
patient_condition_association = None
condition_symptom_association = None

class Patient(Base):
    """Patient model representing a person receiving medical care."""
    __tablename__ = 'patient'

    id = Column(String(36), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(DateTime)
    gender = Column(String(50))
    has_eds = Column(Boolean, default=False)
    eds_type = Column(String(50), nullable=True)
    has_neurodivergence = Column(Boolean, default=False)
    neurodivergence_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize a patient with the given attributes."""
        if 'name' in kwargs:
            # Split name into first and last if only name is provided
            name_parts = kwargs.pop('name').split(' ', 1)
            self.first_name = name_parts[0]
            self.last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Set all other attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Set default ID if not provided
        if not hasattr(self, 'id') or self.id is None:
            self.id = str(uuid.uuid4())
        
        # Set timestamps if not provided
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now()
        
        self.updated_at = datetime.now()

    @property
    def name(self):
        """Return the patient's full name."""
        return f"{self.first_name} {self.last_name}"

class HealthcareProvider(Base):
    """Healthcare provider model representing a doctor or other provider."""
    __tablename__ = 'healthcare_provider'

    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    specialty = Column(String(100))
    facility = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize a healthcare provider with the given attributes."""
        # Handle specialty vs specialties field differences
        if 'specialty' in kwargs and 'specialties' not in kwargs:
            kwargs['specialty'] = kwargs['specialty']
        
        # Set all attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Set default ID if not provided
        if not hasattr(self, 'id') or self.id is None:
            self.id = str(uuid.uuid4())
        
        # Set timestamps if not provided
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now()
        
        self.updated_at = datetime.now()

class Document(Base):
    """Document model representing a medical document."""
    __tablename__ = 'document'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey('patient.id'))
    provider_id = Column(String(36), ForeignKey('healthcare_provider.id'), nullable=True)
    document_type = Column(String(50))  # e.g., 'lab_report', 'clinical_note', 'imaging'
    document_date = Column(DateTime)
    content = Column(Text)
    source = Column(String(100))  # e.g., 'Novant Health', 'Atrium'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in setup_relationships() to avoid circular dependencies

class Condition(Base):
    """Condition model representing a medical condition or diagnosis."""
    __tablename__ = 'condition'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100))
    description = Column(Text)
    icd10_code = Column(String(20))
    is_chronic = Column(Boolean, default=False)
    document_id = Column(String(36), ForeignKey('document.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in setup_relationships() to avoid circular dependencies

class Medication(Base):
    """Medication model representing a medication or treatment."""
    __tablename__ = 'medication'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100))
    dosage = Column(String(50))
    frequency = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    document_id = Column(String(36), ForeignKey('document.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in setup_relationships() to avoid circular dependencies

class Symptom(Base):
    """Symptom model representing a reported symptom."""
    __tablename__ = 'symptom'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100))
    description = Column(Text)
    severity = Column(Integer)
    onset_date = Column(DateTime)
    resolution_date = Column(DateTime)
    is_chronic = Column(Boolean, default=False)
    document_id = Column(String(36), ForeignKey('document.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in setup_relationships() to avoid circular dependencies

class LabResult(Base):
    """Lab result model representing medical test results."""
    __tablename__ = 'lab_result'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_name = Column(String(100))
    test_date = Column(DateTime)
    result_value = Column(String(50))
    unit = Column(String(20))
    reference_range = Column(String(50))
    is_abnormal = Column(Boolean)
    document_id = Column(String(36), ForeignKey('document.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships are defined in setup_relationships() to avoid circular dependencies

class MedicalEvent(Base):
    """Medical event model representing appointments, procedures, etc."""
    __tablename__ = 'medical_event'

    id = Column(String(36), primary_key=True)
    event_type = Column(String(50))
    description = Column(Text)
    event_date = Column(DateTime)
    location = Column(String(200))
    provider_id = Column(String(36), ForeignKey('healthcare_provider.id'))
    patient_id = Column(String(36), ForeignKey('patient.id'))
    document_id = Column(String(36), ForeignKey('document.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize a medical event with the given attributes."""
        # Set all attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Set default ID if not provided
        if not hasattr(self, 'id') or self.id is None:
            self.id = str(uuid.uuid4())
        
        # Set timestamps if not provided
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now()
        
        self.updated_at = datetime.now()

# Define association tables and add relationships after all models are defined
def setup_relationships():
    """
    Set up relationships and association tables after all models are defined
    to avoid circular import issues.
    """
    global event_condition_association, event_medication_association, event_symptom_association
    global event_provider_association, patient_condition_association, condition_symptom_association
    
    # Define association tables
    event_condition_association = Table(
        'event_condition_association', Base.metadata,
        Column('event_id', String(36), ForeignKey('medical_event.id'), primary_key=True),
        Column('condition_id', String(36), ForeignKey('condition.id'), primary_key=True)
    )

    event_medication_association = Table(
        'event_medication_association', Base.metadata,
        Column('event_id', String(36), ForeignKey('medical_event.id'), primary_key=True),
        Column('medication_id', String(36), ForeignKey('medication.id'), primary_key=True)
    )

    event_symptom_association = Table(
        'event_symptom_association', Base.metadata,
        Column('event_id', String(36), ForeignKey('medical_event.id'), primary_key=True),
        Column('symptom_id', String(36), ForeignKey('symptom.id'), primary_key=True)
    )

    event_provider_association = Table(
        'event_provider_association', Base.metadata,
        Column('event_id', String(36), ForeignKey('medical_event.id'), primary_key=True),
        Column('provider_id', String(36), ForeignKey('healthcare_provider.id'), primary_key=True)
    )

    patient_condition_association = Table(
        'patient_condition_association', Base.metadata,
        Column('patient_id', String(36), ForeignKey('patient.id'), primary_key=True),
        Column('condition_id', String(36), ForeignKey('condition.id'), primary_key=True)
    )

    condition_symptom_association = Table(
        'condition_symptom_association', Base.metadata,
        Column('condition_id', String(36), ForeignKey('condition.id'), primary_key=True),
        Column('symptom_id', String(36), ForeignKey('symptom.id'), primary_key=True)
    )
    
    # Add relationships
    Patient.documents = relationship("Document", back_populates="patient")
    Document.patient = relationship("Patient", back_populates="documents")
    Document.provider = relationship("HealthcareProvider")
    Condition.document = relationship("Document")
    Medication.document = relationship("Document")
    Symptom.document = relationship("Document")
    LabResult.document = relationship("Document")
    
    MedicalEvent.provider = relationship("HealthcareProvider")
    MedicalEvent.patient = relationship("Patient")
    MedicalEvent.document = relationship("Document")
    MedicalEvent.conditions = relationship("Condition", secondary=event_condition_association)
    MedicalEvent.medications = relationship("Medication", secondary=event_medication_association)
    MedicalEvent.symptoms = relationship("Symptom", secondary=event_symptom_association)

# Call setup_relationships to initialize tables and relationships
setup_relationships() 