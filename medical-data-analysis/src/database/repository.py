"""
Repository module for database operations.

This module provides an abstract base class for repository implementations
as well as concrete repositories for specific entity types.
"""

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Type, Dict, Any, Union
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, Query
from sqlalchemy import desc, asc

from src.database.connection import get_db
from src.database.models.entity import (
    Patient, HealthcareProvider, MedicalEvent, Condition, 
    Medication, Symptom, LabResult, Document
)

# Type variable for generic repository
T = TypeVar('T')

# Set up logging
logger = logging.getLogger(__name__)


class BaseRepository(Generic[T], ABC):
    """Abstract base repository for database operations."""
    
    @abstractmethod
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository.
        
        Args:
            model_class: The SQLAlchemy model class
        """
        self.model_class = model_class
    
    @abstractmethod
    def get_by_id(self, item_id: str) -> Optional[T]:
        """
        Get an entity by ID.
        
        Args:
            item_id: The ID of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_all(self) -> List[T]:
        """
        List all entities.
        
        Returns:
            List of all entities
        """
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.
        
        Args:
            data: Dictionary with entity data
            
        Returns:
            The created entity
        """
        pass
    
    @abstractmethod
    def update(self, item_id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            item_id: The ID of the entity
            data: Dictionary with updated data
            
        Returns:
            The updated entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            item_id: The ID of the entity
            
        Returns:
            True if deleted, False if not found
        """
        pass


class SQLAlchemyRepository(BaseRepository[T]):
    """SQLAlchemy implementation of the repository pattern."""
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository.
        
        Args:
            model_class: The SQLAlchemy model class
        """
        self.model_class = model_class
    
    def get_by_id(self, item_id: str) -> Optional[T]:
        """
        Get an entity by ID.
        
        Args:
            item_id: The ID of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(self.model_class.id == item_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID: {e}")
            return None
    
    def list_all(self) -> List[T]:
        """
        List all entities.
        
        Returns:
            List of all entities
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).all()
        except SQLAlchemyError as e:
            logger.error(f"Error listing all {self.model_class.__name__}: {e}")
            return []
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.
        
        Args:
            data: Dictionary with entity data
            
        Returns:
            The created entity
        """
        try:
            with get_db() as db:
                entity = self.model_class(**data)
                db.add(entity)
                db.commit()
                db.refresh(entity)
                return entity
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise
    
    def update(self, item_id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            item_id: The ID of the entity
            data: Dictionary with updated data
            
        Returns:
            The updated entity if found, None otherwise
        """
        try:
            with get_db() as db:
                entity = db.query(self.model_class).filter(self.model_class.id == item_id).first()
                if not entity:
                    return None
                
                for key, value in data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                
                db.commit()
                db.refresh(entity)
                return entity
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model_class.__name__}: {e}")
            raise
    
    def delete(self, item_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            item_id: The ID of the entity
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with get_db() as db:
                entity = db.query(self.model_class).filter(self.model_class.id == item_id).first()
                if not entity:
                    return False
                
                db.delete(entity)
                db.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model_class.__name__}: {e}")
            raise
    
    def query(self) -> Query:
        """
        Get a query object for more complex queries.
        
        Returns:
            SQLAlchemy Query object
        """
        try:
            with get_db() as db:
                return db.query(self.model_class)
        except SQLAlchemyError as e:
            logger.error(f"Error creating query for {self.model_class.__name__}: {e}")
            raise


# Specific repositories for different entity types
class PatientRepository(SQLAlchemyRepository[Patient]):
    """Repository for Patient entities."""
    
    def __init__(self):
        super().__init__(Patient)


class HealthcareProviderRepository(SQLAlchemyRepository[HealthcareProvider]):
    """Repository for HealthcareProvider entities."""
    
    def __init__(self):
        super().__init__(HealthcareProvider)
    
    def find_by_name(self, name: str) -> List[HealthcareProvider]:
        """
        Find healthcare providers by name.
        
        Args:
            name: Provider name or partial name
            
        Returns:
            List of matching providers
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.name.ilike(f"%{name}%")
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding providers by name: {e}")
            return []
    
    def find_by_specialty(self, specialty: str) -> List[HealthcareProvider]:
        """
        Find healthcare providers by specialty.
        
        Args:
            specialty: Medical specialty
            
        Returns:
            List of matching providers
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.specialties.ilike(f"%{specialty}%")
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding providers by specialty: {e}")
            return []


class MedicalEventRepository(SQLAlchemyRepository[MedicalEvent]):
    """Repository for MedicalEvent entities."""
    
    def __init__(self):
        super().__init__(MedicalEvent)
    
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[MedicalEvent]:
        """
        Find medical events within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of matching medical events
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.event_date >= start_date,
                    self.model_class.event_date <= end_date
                ).order_by(asc(self.model_class.event_date)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding events by date range: {e}")
            return []
    
    def find_by_patient(self, patient_id: str) -> List[MedicalEvent]:
        """
        Find medical events for a specific patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of matching medical events
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.patient_id == patient_id
                ).order_by(asc(self.model_class.event_date)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding events by patient: {e}")
            return []
    
    def find_by_type(self, event_type: str, patient_id: Optional[str] = None) -> List[MedicalEvent]:
        """
        Find medical events by type.
        
        Args:
            event_type: Type of event (appointment, procedure, etc.)
            patient_id: Optional patient ID to filter by
            
        Returns:
            List of matching medical events
        """
        try:
            with get_db() as db:
                query = db.query(self.model_class).filter(
                    self.model_class.event_type == event_type
                )
                
                if patient_id:
                    query = query.filter(self.model_class.patient_id == patient_id)
                
                return query.order_by(asc(self.model_class.event_date)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding events by type: {e}")
            return []


class ConditionRepository(SQLAlchemyRepository[Condition]):
    """Repository for Condition entities."""
    
    def __init__(self):
        super().__init__(Condition)
    
    def find_by_name(self, name: str) -> List[Condition]:
        """
        Find conditions by name.
        
        Args:
            name: Condition name or partial name
            
        Returns:
            List of matching conditions
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.name.ilike(f"%{name}%")
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding conditions by name: {e}")
            return []


class MedicationRepository(SQLAlchemyRepository[Medication]):
    """Repository for Medication entities."""
    
    def __init__(self):
        super().__init__(Medication)
    
    def find_active_medications(self) -> List[Medication]:
        """
        Find all active medications.
        
        Returns:
            List of active medications
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.is_active == True
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding active medications: {e}")
            return []


class SymptomRepository(SQLAlchemyRepository[Symptom]):
    """Repository for Symptom entities."""
    
    def __init__(self):
        super().__init__(Symptom)
    
    def find_by_body_system(self, body_system: str) -> List[Symptom]:
        """
        Find symptoms by body system.
        
        Args:
            body_system: Body system (e.g., cardiovascular, neurological)
            
        Returns:
            List of matching symptoms
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.body_system.ilike(f"%{body_system}%")
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding symptoms by body system: {e}")
            return []


class LabResultRepository(SQLAlchemyRepository[LabResult]):
    """Repository for LabResult entities."""
    
    def __init__(self):
        super().__init__(LabResult)
    
    def find_abnormal_results(self) -> List[LabResult]:
        """
        Find all abnormal lab results.
        
        Returns:
            List of abnormal lab results
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.is_abnormal == True
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding abnormal lab results: {e}")
            return []
    
    def find_by_test_name(self, test_name: str) -> List[LabResult]:
        """
        Find lab results by test name.
        
        Args:
            test_name: Test name or partial name
            
        Returns:
            List of matching lab results
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.test_name.ilike(f"%{test_name}%")
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding lab results by test name: {e}")
            return []


class DocumentRepository(SQLAlchemyRepository[Document]):
    """Repository for Document entities."""
    
    def __init__(self):
        super().__init__(Document)
    
    def find_by_document_type(self, document_type: str) -> List[Document]:
        """
        Find documents by document type.
        
        Args:
            document_type: Type of document (lab_report, clinical_note, etc.)
            
        Returns:
            List of matching documents
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.document_type == document_type
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding documents by type: {e}")
            return []
    
    def find_unprocessed_documents(self) -> List[Document]:
        """
        Find all unprocessed documents.
        
        Returns:
            List of unprocessed documents
        """
        try:
            with get_db() as db:
                return db.query(self.model_class).filter(
                    self.model_class.is_processed == False
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding unprocessed documents: {e}")
            return [] 