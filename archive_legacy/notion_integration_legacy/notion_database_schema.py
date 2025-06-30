"""
Notion Database Schema

This module defines the schema for Notion databases used in the medical data integration.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum


class NotionPropertyType(Enum):
    """Types of properties in Notion databases"""
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"


class NotionDatabaseType(Enum):
    """Types of medical databases in Notion"""
    MEDICAL_CALENDAR = "medical_calendar"
    MEDICAL_TEAM = "medical_team"
    MEDICAL_CONDITIONS = "medical_conditions"
    MEDICATIONS = "medications"
    SYMPTOMS = "symptoms"


class NotionDatabaseSchema:
    """Schema definition for a Notion database"""
    
    def __init__(self, name: str, properties: Dict[str, Dict[str, Any]]):
        """
        Initialize a database schema
        
        Args:
            name: Name of the database
            properties: Dictionary of property definitions
        """
        self.name = name
        self.properties = properties


# Schema definitions for various medical database types

# Medical Calendar Schema (Appointments)
MEDICAL_CALENDAR_SCHEMA = NotionDatabaseSchema(
    name="Medical Calendar",
    properties={
        "Name": {
            "type": NotionPropertyType.TITLE,
            "required": True,
            "description": "Title of the appointment"
        },
        "Date": {
            "type": NotionPropertyType.DATE,
            "required": True,
            "description": "Date and time of the appointment"
        },
        "Doctor": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Relation to the doctor/provider in Medical Team database"
        },
        "Type": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Type of appointment (e.g., Initial, Follow-up, Testing)"
        },
        "Status": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Status of the appointment (e.g., Scheduled, Completed, Cancelled)"
        },
        "Notes": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Notes about the appointment"
        },
        "Location": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Location of the appointment"
        },
        "Symptoms": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Related symptoms discussed"
        },
        "Conditions": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Related conditions discussed"
        },
        "Attachments": {
            "type": NotionPropertyType.FILES,
            "required": False,
            "description": "Files related to the appointment (e.g., lab results, imaging)"
        }
    }
)

# Medical Team Schema (Doctors/Providers)
MEDICAL_TEAM_SCHEMA = NotionDatabaseSchema(
    name="Medical Team",
    properties={
        "Name": {
            "type": NotionPropertyType.TITLE,
            "required": True,
            "description": "Name of the doctor/provider"
        },
        "Specialty": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Medical specialty"
        },
        "Contact": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Contact information"
        },
        "Office": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Office location or practice name"
        },
        "First Visit": {
            "type": NotionPropertyType.DATE,
            "required": False,
            "description": "Date of first visit"
        },
        "Appointments": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Related appointments with this provider"
        },
        "Notes": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Notes about this provider"
        },
        "Status": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Current status (e.g., Active, Inactive, Referred)"
        },
        "Conditions": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Conditions this provider is treating"
        },
        "id": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Internal ID for reference"
        }
    }
)

# Medical Conditions Schema
MEDICAL_CONDITIONS_SCHEMA = NotionDatabaseSchema(
    name="Medical Conditions",
    properties={
        "Name": {
            "type": NotionPropertyType.TITLE,
            "required": True,
            "description": "Name of the condition"
        },
        "Status": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Status of the condition (e.g., Diagnosed, Suspected, Ruled Out)"
        },
        "Date Diagnosed": {
            "type": NotionPropertyType.DATE,
            "required": False,
            "description": "Date when the condition was diagnosed"
        },
        "Diagnosing Doctor": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Doctor who diagnosed the condition"
        },
        "Treating Doctors": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Doctors treating this condition"
        },
        "Symptoms": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Symptoms associated with this condition"
        },
        "Medications": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Medications prescribed for this condition"
        },
        "Related Appointments": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Appointments related to this condition"
        },
        "Notes": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Notes about this condition"
        },
        "ICD-10 Code": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "ICD-10 diagnostic code"
        },
        "Category": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Category of condition (e.g., Autoimmune, Neurological, Musculoskeletal)"
        }
    }
)

# Medications Schema
MEDICATIONS_SCHEMA = NotionDatabaseSchema(
    name="Medications",
    properties={
        "Name": {
            "type": NotionPropertyType.TITLE,
            "required": True,
            "description": "Name of the medication"
        },
        "Generic Name": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Generic name of the medication"
        },
        "Dosage": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Dosage information"
        },
        "Frequency": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "How often the medication is taken"
        },
        "Start Date": {
            "type": NotionPropertyType.DATE,
            "required": False,
            "description": "Date started taking this medication"
        },
        "End Date": {
            "type": NotionPropertyType.DATE,
            "required": False,
            "description": "Date stopped taking this medication"
        },
        "Prescribing Doctor": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Doctor who prescribed this medication"
        },
        "For Conditions": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Conditions this medication is treating"
        },
        "Side Effects": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Side effects experienced"
        },
        "Notes": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Notes about this medication"
        },
        "Status": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Status (e.g., Current, Discontinued, As Needed)"
        },
        "Category": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Category of medication"
        }
    }
)

# Symptoms Schema
SYMPTOMS_SCHEMA = NotionDatabaseSchema(
    name="Symptoms",
    properties={
        "Name": {
            "type": NotionPropertyType.TITLE,
            "required": True,
            "description": "Name of the symptom"
        },
        "First Occurrence": {
            "type": NotionPropertyType.DATE,
            "required": False,
            "description": "Date when the symptom was first experienced"
        },
        "Severity": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Severity of the symptom (e.g., Mild, Moderate, Severe)"
        },
        "Frequency": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Frequency of the symptom (e.g., Constant, Intermittent, Rare)"
        },
        "Associated Conditions": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Conditions associated with this symptom"
        },
        "Discussed With Doctors": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Doctors this symptom has been discussed with"
        },
        "Appointments": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Appointments where this symptom was discussed"
        },
        "Relieved By": {
            "type": NotionPropertyType.RELATION,
            "required": False,
            "description": "Medications or treatments that relieve this symptom"
        },
        "Triggered By": {
            "type": NotionPropertyType.MULTI_SELECT,
            "required": False,
            "description": "Factors that trigger or worsen this symptom"
        },
        "Notes": {
            "type": NotionPropertyType.RICH_TEXT,
            "required": False,
            "description": "Notes about this symptom"
        },
        "Body System": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Body system affected (e.g., Neurological, Digestive, Musculoskeletal)"
        },
        "Status": {
            "type": NotionPropertyType.SELECT,
            "required": False,
            "description": "Current status (e.g., Active, Resolved, Intermittent)"
        }
    }
)

# Map of database types to schema definitions
DATABASE_SCHEMAS = {
    NotionDatabaseType.MEDICAL_CALENDAR.value: MEDICAL_CALENDAR_SCHEMA,
    NotionDatabaseType.MEDICAL_TEAM.value: MEDICAL_TEAM_SCHEMA,
    NotionDatabaseType.MEDICAL_CONDITIONS.value: MEDICAL_CONDITIONS_SCHEMA,
    NotionDatabaseType.MEDICATIONS.value: MEDICATIONS_SCHEMA,
    NotionDatabaseType.SYMPTOMS.value: SYMPTOMS_SCHEMA
}

# Map database type strings to enum values
DATABASE_TYPE_MAP = {
    "medical_calendar": NotionDatabaseType.MEDICAL_CALENDAR,
    "medical_team": NotionDatabaseType.MEDICAL_TEAM,
    "medical_conditions": NotionDatabaseType.MEDICAL_CONDITIONS,
    "medications": NotionDatabaseType.MEDICATIONS,
    "symptoms": NotionDatabaseType.SYMPTOMS
}

# Helper functions for database schema operations
def get_schema_for_database(database_type: str) -> Optional[NotionDatabaseSchema]:
    """
    Get the schema for a database type
    
    Args:
        database_type: Type of database
        
    Returns:
        Database schema or None if not found
    """
    return DATABASE_SCHEMAS.get(database_type)


def get_property_type(database_type: str, property_name: str) -> Optional[NotionPropertyType]:
    """
    Get the type of a property in a database
    
    Args:
        database_type: Type of database
        property_name: Name of the property
        
    Returns:
        Property type or None if not found
    """
    schema = get_schema_for_database(database_type)
    if not schema or property_name not in schema.properties:
        return None
        
    return schema.properties[property_name]["type"]


def validate_entity_data(database_type: str, entity_data: Dict[str, Any]) -> List[str]:
    """
    Validate entity data against a database schema
    
    Args:
        database_type: Type of database
        entity_data: Entity data to validate
        
    Returns:
        List of validation errors, empty if valid
    """
    schema = get_schema_for_database(database_type)
    if not schema:
        return [f"Unknown database type: {database_type}"]
        
    errors = []
    
    # Check required properties
    for prop_name, prop_def in schema.properties.items():
        if prop_def.get("required", False) and (prop_name not in entity_data or not entity_data[prop_name]):
            errors.append(f"Required property '{prop_name}' is missing")
    
    return errors 