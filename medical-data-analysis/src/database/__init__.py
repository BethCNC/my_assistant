"""
Database module for medical data storage and retrieval.

This package contains all database-related functionality including:
- Database connection and session management
- Model definitions for medical entities
- Query interfaces for retrieving medical data
"""

from src.database.connection import engine, Session, Base

__all__ = ['engine', 'Session', 'Base'] 