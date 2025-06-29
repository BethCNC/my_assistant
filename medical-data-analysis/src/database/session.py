"""
Database Session Manager Stub

This is a minimal stub implementation to allow the pipeline to initialize
without a full database setup for testing purposes.
"""

import logging

logger = logging.getLogger(__name__)

class StubQuery:
    """Stub query class for mock SQLAlchemy queries."""
    
    def __init__(self, model_class):
        self.model_class = model_class
        
    def filter(self, *args, **kwargs):
        """Stub filter method."""
        return self
        
    def first(self):
        """Return None for first item."""
        return None
        
    def all(self):
        """Return empty list for all items."""
        return []

class DatabaseSession:
    """Stub database session manager for testing."""
    
    def __init__(self, connection_string=None):
        """Initialize the database session."""
        self.connection_string = connection_string or "sqlite:///:memory:"
        logger.info(f"Initialized stub database session with {self.connection_string}")
        self.is_connected = True
    
    def store_document(self, document):
        """Stub method to store a document."""
        logger.info(f"Stub: Storing document {getattr(document, 'id', 'unknown')}")
        return True
    
    def store_entity(self, entity, entity_type):
        """Stub method to store an entity."""
        logger.info(f"Stub: Storing {entity_type} entity")
        return True
    
    def get_document(self, document_id):
        """Stub method to retrieve a document."""
        logger.info(f"Stub: Retrieving document {document_id}")
        return None
    
    def query(self, model_class):
        """Stub query method for SQLAlchemy compatibility."""
        return StubQuery(model_class)
    
    def add(self, entity):
        """Stub add method for SQLAlchemy compatibility."""
        logger.info(f"Stub: Adding entity to session")
        return True
    
    def commit(self):
        """Stub commit method for SQLAlchemy compatibility."""
        logger.info(f"Stub: Committing session")
        return True
    
    def rollback(self):
        """Stub rollback method for SQLAlchemy compatibility."""
        logger.info(f"Stub: Rolling back session")
        return True
    
    def delete(self, entity):
        """Stub delete method for SQLAlchemy compatibility."""
        logger.info(f"Stub: Deleting entity from session")
        return True
    
    def close(self):
        """Close the database session."""
        logger.info("Stub: Closing database session")
        self.is_connected = False

def create_session(connection_string=None):
    """Create a new database session."""
    return DatabaseSession(connection_string)

# Add the get_session function that the pipeline is importing
def get_session(connection_string=None):
    """Get a database session.
    
    This is an alias for create_session for backward compatibility.
    """
    return create_session(connection_string) 