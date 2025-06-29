"""
Database initialization script.

This script creates all database tables and initializes
any required reference data.
"""

import logging
from pathlib import Path
import uuid
from datetime import datetime

from src.database.connection import engine, Base, Session
from src.database.models.entity import Patient  # Import all models explicitly

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize the database by creating all tables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize test patient
        init_test_data()
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False


def init_test_data():
    """Initialize test data for development."""
    try:
        logger.info("Initializing test data...")
        db = Session()
        
        # Check if test patient exists
        test_patient = db.query(Patient).filter_by(name="Test Patient").first()
        
        if not test_patient:
            test_patient = Patient(
                id=str(uuid.uuid4()),
                name="Test Patient",
                date_of_birth=datetime(1980, 1, 1),
                gender="female",
                has_eds=True,
                eds_type="hypermobile",
                has_neurodivergence=True,
                neurodivergence_type="ADHD"
            )
            db.add(test_patient)
            db.commit()
            logger.info("Test patient created successfully")
        else:
            logger.info("Test patient already exists")
            
    except Exception as e:
        logger.error(f"Error initializing test data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # When run directly, initialize the database
    success = init_db()
    if success:
        logger.info("Database initialization complete")
    else:
        logger.error("Database initialization failed") 