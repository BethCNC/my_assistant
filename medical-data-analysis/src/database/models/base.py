"""
Base models for database entities.

Contains the Base model with common fields for all database entities
such as creation time, update time, and unique identifiers.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Boolean
from sqlalchemy.ext.declarative import declared_attr

from src.database.connection import Base


class BaseModel:
    """Base model for all database entities with common fields."""
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Source tracking
    source_document = Column(String(255), nullable=True, index=True)
    source_type = Column(String(50), nullable=True)
    
    # Confidence and verification
    confidence_score = Column(String(10), nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    
    def __repr__(self):
        """Return string representation of the model."""
        return f"<{self.__class__.__name__} {self.id}>" 