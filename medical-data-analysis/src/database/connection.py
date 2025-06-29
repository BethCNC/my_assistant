"""
Database connection configuration using SQLAlchemy.

This module sets up the SQLAlchemy engine, session, and base class
for declarative models.
"""

import os
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession

from src.config.settings import DATABASE_URI

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URI,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create session factory
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

@contextmanager
def get_db() -> Generator[SQLAlchemySession, None, None]:
    """
    Get a database session with automatic commit/rollback and cleanup.
    
    Yields:
        SQLAlchemy Session: Database session
        
    Raises:
        Exception: Any exception that occurs during database operations
    """
    db = Session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Add alias for compatibility
get_db_session = get_db 