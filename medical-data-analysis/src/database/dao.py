#!/usr/bin/env python
"""
Data Access Objects (DAOs) for database operations.

This module provides DAOs for each entity type, handling CRUD operations
and common queries for the medical database.
"""

from typing import List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.database.models.entity import (
    Document, Patient, HealthcareProvider, Condition, 
    Medication, Symptom, MedicalEvent, LabResult
)

logger = logging.getLogger(__name__)

class BaseDAO:
    """Base Data Access Object with common CRUD operations."""
    
    def __init__(self, session: Session, model_class: Any):
        """
        Initialize the DAO with a database session and model class.
        
        Args:
            session: SQLAlchemy session for database operations
            model_class: The SQLAlchemy model class this DAO will handle
        """
        self.session = session
        self.model_class = model_class
    
    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Entity object if found, None otherwise
        """
        try:
            return self.session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {self.model_class.__name__} with ID {entity_id}: {str(e)}")
            return None
    
    def get_all(self) -> List[Any]:
        """
        Get all entities of this type.
        
        Returns:
            List of all entity objects
        """
        try:
            return self.session.query(self.model_class).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all {self.model_class.__name__} objects: {str(e)}")
            return []
    
    def create(self, entity: Any) -> Optional[int]:
        """
        Create a new entity in the database.
        
        Args:
            entity: Entity object to create
            
        Returns:
            ID of the created entity, or None if creation failed
        """
        try:
            self.session.add(entity)
            self.session.commit()
            return entity.id
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            return None
    
    def update(self, entity: Any) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: Entity object to update
            
        Returns:
            True if update succeeded, False otherwise
        """
        try:
            self.session.add(entity)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model_class.__name__} with ID {entity.id}: {str(e)}")
            return False
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        try:
            entity = self.get_by_id(entity_id)
            if entity:
                self.session.delete(entity)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} with ID {entity_id}: {str(e)}")
            return False


class DocumentDAO(BaseDAO):
    """DAO for Document entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, Document)
    
    def get_by_file_path(self, file_path: str) -> Optional[Document]:
        """Get a document by its file path."""
        try:
            return self.session.query(Document).filter(
                Document.file_path == file_path
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Document with file path {file_path}: {str(e)}")
            return None
    
    def get_by_patient_id(self, patient_id: int) -> List[Document]:
        """Get all documents for a patient."""
        try:
            return self.session.query(Document).filter(
                Document.patient_id == patient_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Documents for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_document_type(self, document_type: str) -> List[Document]:
        """Get all documents of a specific type."""
        try:
            return self.session.query(Document).filter(
                Document.document_type == document_type
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Documents of type {document_type}: {str(e)}")
            return []


class PatientDAO(BaseDAO):
    """DAO for Patient entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, Patient)
    
    def get_by_name(self, name: str) -> Optional[Patient]:
        """Get a patient by name."""
        try:
            return self.session.query(Patient).filter(
                Patient.name == name
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Patient with name {name}: {str(e)}")
            return None
    
    def get_by_mrn(self, mrn: str) -> Optional[Patient]:
        """Get a patient by medical record number."""
        try:
            return self.session.query(Patient).filter(
                Patient.medical_record_number == mrn
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Patient with MRN {mrn}: {str(e)}")
            return None


class ProviderDAO(BaseDAO):
    """DAO for HealthcareProvider entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, HealthcareProvider)
    
    def get_by_name(self, name: str) -> Optional[HealthcareProvider]:
        """Get a provider by name."""
        try:
            return self.session.query(HealthcareProvider).filter(
                HealthcareProvider.name == name
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving HealthcareProvider with name {name}: {str(e)}")
            return None
    
    def get_by_specialty(self, specialty: str) -> List[HealthcareProvider]:
        """Get all providers with a specific specialty."""
        try:
            return self.session.query(HealthcareProvider).filter(
                HealthcareProvider.specialty == specialty
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving HealthcareProviders with specialty {specialty}: {str(e)}")
            return []


class ConditionDAO(BaseDAO):
    """DAO for Condition entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, Condition)
    
    def get_by_patient_id(self, patient_id: int) -> List[Condition]:
        """Get all conditions for a patient."""
        try:
            return self.session.query(Condition).filter(
                Condition.patient_id == patient_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Conditions for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_name(self, name: str) -> List[Condition]:
        """Get all conditions with a specific name."""
        try:
            return self.session.query(Condition).filter(
                Condition.name == name
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Conditions with name {name}: {str(e)}")
            return []


class MedicationDAO(BaseDAO):
    """DAO for Medication entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, Medication)
    
    def get_by_patient_id(self, patient_id: int) -> List[Medication]:
        """Get all medications for a patient."""
        try:
            return self.session.query(Medication).filter(
                Medication.patient_id == patient_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Medications for patient {patient_id}: {str(e)}")
            return []
    
    def get_active_medications(self, patient_id: int) -> List[Medication]:
        """Get all active medications for a patient."""
        try:
            return self.session.query(Medication).filter(
                Medication.patient_id == patient_id,
                Medication.is_active == True
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving active Medications for patient {patient_id}: {str(e)}")
            return []


class SymptomDAO(BaseDAO):
    """DAO for Symptom entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, Symptom)
    
    def get_by_patient_id(self, patient_id: int) -> List[Symptom]:
        """Get all symptoms for a patient."""
        try:
            return self.session.query(Symptom).filter(
                Symptom.patient_id == patient_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Symptoms for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_body_system(self, body_system: str) -> List[Symptom]:
        """Get all symptoms related to a specific body system."""
        try:
            return self.session.query(Symptom).filter(
                Symptom.body_system == body_system
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving Symptoms for body system {body_system}: {str(e)}")
            return []
    
    def get_active_symptoms(self, patient_id: int) -> List[Symptom]:
        """Get all active symptoms for a patient."""
        try:
            return self.session.query(Symptom).filter(
                Symptom.patient_id == patient_id,
                Symptom.status == "active"
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving active Symptoms for patient {patient_id}: {str(e)}")
            return []


class MedicalEventDAO(BaseDAO):
    """DAO for MedicalEvent entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, MedicalEvent)
    
    def get_by_patient_id(self, patient_id: int) -> List[MedicalEvent]:
        """Get all medical events for a patient."""
        try:
            return self.session.query(MedicalEvent).filter(
                MedicalEvent.patient_id == patient_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving MedicalEvents for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_date_range(self, patient_id: int, start_date: str, end_date: str) -> List[MedicalEvent]:
        """Get all medical events for a patient within a date range."""
        try:
            return self.session.query(MedicalEvent).filter(
                MedicalEvent.patient_id == patient_id,
                MedicalEvent.event_date >= start_date,
                MedicalEvent.event_date <= end_date
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving MedicalEvents for patient {patient_id} in date range: {str(e)}")
            return []


class LabResultDAO(BaseDAO):
    """DAO for LabResult entities."""
    
    def __init__(self, session: Session):
        super().__init__(session, LabResult)
    
    def get_by_patient_id(self, patient_id: int) -> List[LabResult]:
        """Get all lab results for a patient."""
        try:
            return self.session.query(LabResult).filter(
                LabResult.patient_id == patient_id
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving LabResults for patient {patient_id}: {str(e)}")
            return []
    
    def get_by_test_name(self, patient_id: int, test_name: str) -> List[LabResult]:
        """Get all lab results for a specific test for a patient."""
        try:
            return self.session.query(LabResult).filter(
                LabResult.patient_id == patient_id,
                LabResult.test_name == test_name
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving LabResults for patient {patient_id} and test {test_name}: {str(e)}")
            return [] 