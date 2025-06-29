"""
Notion Entity Mapper

This module maps extracted medical entities to Notion database properties
with consistent naming and structure.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class NotionEntityMapper:
    """Maps extracted medical entities to Notion database properties."""
    
    def __init__(self, config=None):
        """
        Initialize the entity mapper with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def map_entity_to_notion_properties(self, entity: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Map an extracted entity to appropriate Notion database properties.
        
        Args:
            entity: The entity object with extracted properties
            entity_type: Type of entity (appointment, doctor, medication, etc.)
            
        Returns:
            Dictionary of Notion-formatted properties
        """
        properties = {}
        
        # First, add standard properties based on entity type
        if entity_type == "doctors":
            properties = self._map_doctor_properties(entity)
        elif entity_type == "appointments":
            properties = self._map_appointment_properties(entity)
        elif entity_type == "medications":
            properties = self._map_medication_properties(entity)
        elif entity_type == "conditions":
            properties = self._map_condition_properties(entity)
        elif entity_type == "symptoms":
            properties = self._map_symptom_properties(entity)
        elif entity_type == "lab_results":
            properties = self._map_lab_result_properties(entity)
        elif entity_type == "procedures":
            properties = self._map_procedure_properties(entity)
        elif entity_type == "documents":
            properties = self._map_document_properties(entity)
        else:
            # Generic mapping for unknown entity types
            self.logger.warning(f"Unknown entity type: {entity_type}, using generic mapping")
            properties = self._map_generic_properties(entity)
        
        # Add metadata about the source
        if "source_document" in entity and entity["source_document"]:
            properties["Source Document"] = self._format_rich_text(entity["source_document"])
        
        # Add extracted date if present
        if "date" in entity and entity["date"]:
            properties["Date"] = self._format_date(entity["date"])
        
        return properties
    
    def _map_doctor_properties(self, doctor: Dict[str, Any]) -> Dict[str, Any]:
        """Map doctor entity to Notion properties."""
        properties = {
            "Name": self._format_title(self._get_doctor_name(doctor)),
            "Specialty": self._format_select(doctor.get("specialty", "Unknown")),
            "Location": self._format_rich_text(doctor.get("location", "")),
            "Phone": self._format_rich_text(doctor.get("phone", "")),
            "Email": self._format_rich_text(doctor.get("email", "")),
            "Notes": self._format_rich_text(doctor.get("notes", ""))
        }
        
        # Add practice or hospital if present
        if "practice" in doctor and doctor["practice"]:
            properties["Practice"] = self._format_rich_text(doctor["practice"])
        
        return properties
    
    def _map_appointment_properties(self, appointment: Dict[str, Any]) -> Dict[str, Any]:
        """Map appointment entity to Notion properties."""
        # Create a title that includes date and doctor if available
        title_parts = []
        if "date" in appointment and appointment["date"]:
            title_parts.append(appointment["date"])
        if "doctor_name" in appointment and appointment["doctor_name"]:
            title_parts.append(f"Dr. {appointment['doctor_name']}")
        if "specialty" in appointment and appointment["specialty"]:
            title_parts.append(appointment["specialty"])
        
        title = " - ".join(title_parts) if title_parts else "Appointment"
        
        properties = {
            "Name": self._format_title(title),
            "Status": self._format_select(appointment.get("status", "Completed")),
            "Notes": self._format_rich_text(appointment.get("notes", ""))
        }
        
        # Add date if present
        if "date" in appointment and appointment["date"]:
            properties["Date"] = self._format_date(appointment["date"])
            
        # Add time if present
        if "time" in appointment and appointment["time"]:
            properties["Time"] = self._format_rich_text(appointment["time"])
        
        # Add doctor relation if doctor_id is present
        if "doctor_id" in appointment and appointment["doctor_id"]:
            properties["Doctor"] = self._format_relation([appointment["doctor_id"]])
        elif "doctor_name" in appointment and appointment["doctor_name"]:
            properties["Doctor Name"] = self._format_rich_text(appointment["doctor_name"])
        
        # Add location if present
        if "location" in appointment and appointment["location"]:
            properties["Location"] = self._format_rich_text(appointment["location"])
        
        return properties
    
    def _map_medication_properties(self, medication: Dict[str, Any]) -> Dict[str, Any]:
        """Map medication entity to Notion properties."""
        # Create a title that includes medication name and dosage if available
        title_parts = []
        if "name" in medication:
            title_parts.append(medication["name"])
        if "dosage" in medication and medication["dosage"]:
            title_parts.append(medication["dosage"])
        
        title = " - ".join(title_parts) if title_parts else "Medication"
        
        properties = {
            "Name": self._format_title(title),
            "Status": self._format_select(medication.get("status", "Active")),
            "Dosage": self._format_rich_text(medication.get("dosage", "")),
            "Frequency": self._format_rich_text(medication.get("frequency", "")),
            "Notes": self._format_rich_text(medication.get("notes", ""))
        }
        
        # Add start date if present
        if "start_date" in medication and medication["start_date"]:
            properties["Start Date"] = self._format_date(medication["start_date"])
            
        # Add end date if present
        if "end_date" in medication and medication["end_date"]:
            properties["End Date"] = self._format_date(medication["end_date"])
        
        # Add prescribing doctor if present
        if "doctor_id" in medication and medication["doctor_id"]:
            properties["Prescribed By"] = self._format_relation([medication["doctor_id"]])
        elif "doctor_name" in medication and medication["doctor_name"]:
            properties["Doctor Name"] = self._format_rich_text(medication["doctor_name"])
        
        # Add related conditions if present
        if "condition_id" in medication and medication["condition_id"]:
            properties["Related Condition"] = self._format_relation([medication["condition_id"]])
        elif "condition_name" in medication and medication["condition_name"]:
            properties["Condition"] = self._format_rich_text(medication["condition_name"])
        
        return properties
    
    def _map_condition_properties(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        """Map condition entity to Notion properties."""
        properties = {
            "Name": self._format_title(condition.get("name", "Condition")),
            "Status": self._format_select(condition.get("status", "Active")),
            "Notes": self._format_rich_text(condition.get("notes", ""))
        }
        
        # Add diagnosis date if present
        if "diagnosis_date" in condition and condition["diagnosis_date"]:
            properties["Diagnosis Date"] = self._format_date(condition["diagnosis_date"])
        
        # Add diagnosing doctor if present
        if "doctor_id" in condition and condition["doctor_id"]:
            properties["Diagnosed By"] = self._format_relation([condition["doctor_id"]])
        elif "doctor_name" in condition and condition["doctor_name"]:
            properties["Doctor Name"] = self._format_rich_text(condition["doctor_name"])
        
        # Add related symptoms if present as multi-select
        if "symptoms" in condition and condition["symptoms"]:
            symptoms = condition["symptoms"]
            if isinstance(symptoms, list):
                properties["Symptoms"] = self._format_multi_select(symptoms)
            elif isinstance(symptoms, str):
                # Split comma-separated symptoms
                symptom_list = [s.strip() for s in symptoms.split(",")]
                properties["Symptoms"] = self._format_multi_select(symptom_list)
        
        return properties
    
    def _map_symptom_properties(self, symptom: Dict[str, Any]) -> Dict[str, Any]:
        """Map symptom entity to Notion properties."""
        properties = {
            "Name": self._format_title(symptom.get("name", "Symptom")),
            "Severity": self._format_select(symptom.get("severity", "Medium")),
            "Notes": self._format_rich_text(symptom.get("notes", ""))
        }
        
        # Add onset date if present
        if "onset_date" in symptom and symptom["onset_date"]:
            properties["Onset Date"] = self._format_date(symptom["onset_date"])
        
        # Add related condition if present
        if "condition_id" in symptom and symptom["condition_id"]:
            properties["Related Condition"] = self._format_relation([symptom["condition_id"]])
        elif "condition_name" in symptom and symptom["condition_name"]:
            properties["Condition"] = self._format_rich_text(symptom["condition_name"])
        
        # Add body location if present
        if "location" in symptom and symptom["location"]:
            properties["Body Location"] = self._format_rich_text(symptom["location"])
        
        # Add frequency if present
        if "frequency" in symptom and symptom["frequency"]:
            properties["Frequency"] = self._format_select(symptom["frequency"])
        
        return properties
    
    def _map_lab_result_properties(self, lab_result: Dict[str, Any]) -> Dict[str, Any]:
        """Map lab result entity to Notion properties."""
        # Create a title that includes test name and date if available
        title_parts = []
        if "test_name" in lab_result:
            title_parts.append(lab_result["test_name"])
        if "date" in lab_result and lab_result["date"]:
            title_parts.append(lab_result["date"])
        
        title = " - ".join(title_parts) if title_parts else "Lab Result"
        
        properties = {
            "Name": self._format_title(title),
            "Test Name": self._format_rich_text(lab_result.get("test_name", "")),
            "Value": self._format_rich_text(lab_result.get("value", "")),
            "Unit": self._format_rich_text(lab_result.get("unit", "")),
            "Reference Range": self._format_rich_text(lab_result.get("reference_range", "")),
            "Notes": self._format_rich_text(lab_result.get("notes", ""))
        }
        
        # Add date if present
        if "date" in lab_result and lab_result["date"]:
            properties["Date"] = self._format_date(lab_result["date"])
        
        # Add status/flag if present (e.g., "Normal", "High", "Low")
        if "flag" in lab_result and lab_result["flag"]:
            properties["Flag"] = self._format_select(lab_result["flag"])
        
        # Add ordering doctor if present
        if "doctor_id" in lab_result and lab_result["doctor_id"]:
            properties["Ordered By"] = self._format_relation([lab_result["doctor_id"]])
        elif "doctor_name" in lab_result and lab_result["doctor_name"]:
            properties["Doctor Name"] = self._format_rich_text(lab_result["doctor_name"])
        
        # Add related condition if present
        if "condition_id" in lab_result and lab_result["condition_id"]:
            properties["Related Condition"] = self._format_relation([lab_result["condition_id"]])
        
        return properties
    
    def _map_procedure_properties(self, procedure: Dict[str, Any]) -> Dict[str, Any]:
        """Map procedure entity to Notion properties."""
        # Create a title that includes procedure name and date if available
        title_parts = []
        if "name" in procedure:
            title_parts.append(procedure["name"])
        if "date" in procedure and procedure["date"]:
            title_parts.append(procedure["date"])
        
        title = " - ".join(title_parts) if title_parts else "Procedure"
        
        properties = {
            "Name": self._format_title(title),
            "Status": self._format_select(procedure.get("status", "Completed")),
            "Notes": self._format_rich_text(procedure.get("notes", ""))
        }
        
        # Add date if present
        if "date" in procedure and procedure["date"]:
            properties["Date"] = self._format_date(procedure["date"])
        
        # Add location if present
        if "location" in procedure and procedure["location"]:
            properties["Location"] = self._format_rich_text(procedure["location"])
        
        # Add performing doctor if present
        if "doctor_id" in procedure and procedure["doctor_id"]:
            properties["Performed By"] = self._format_relation([procedure["doctor_id"]])
        elif "doctor_name" in procedure and procedure["doctor_name"]:
            properties["Doctor Name"] = self._format_rich_text(procedure["doctor_name"])
        
        # Add related condition if present
        if "condition_id" in procedure and procedure["condition_id"]:
            properties["Related Condition"] = self._format_relation([procedure["condition_id"]])
        
        return properties
    
    def _map_document_properties(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Map document entity to Notion properties."""
        title = document.get("title", "Document")
        
        properties = {
            "Name": self._format_title(title),
            "Type": self._format_select(document.get("extension", "Unknown").replace(".", "").upper()),
            "Path": self._format_rich_text(document.get("path", "")),
            "Word Count": self._format_number(document.get("word_count", 0)),
            "Character Count": self._format_number(document.get("character_count", 0)),
            "Preview": self._format_rich_text(document.get("preview", ""))
        }
        
        # Add document date if present
        if "document_date" in document and document["document_date"]:
            properties["Document Date"] = self._format_date(document["document_date"])
        
        # Add created time if present
        if "created_time" in document and document["created_time"]:
            properties["Created"] = self._format_date(document["created_time"])
        
        # Add modified time if present
        if "modified_time" in document and document["modified_time"]:
            properties["Modified"] = self._format_date(document["modified_time"])
        
        # Add entities found in the document
        entity_types = ["doctors", "appointments", "medications", 
                        "conditions", "symptoms", "lab_results", "procedures"]
        
        for entity_type in entity_types:
            if entity_type in document and document[entity_type]:
                if isinstance(document[entity_type], list):
                    entity_names = [e.get("name", "Unknown") for e in document[entity_type] if "name" in e]
                    if entity_names:
                        properties[entity_type.title()] = self._format_multi_select(entity_names)
        
        return properties
    
    def _map_generic_properties(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Map generic entity to Notion properties."""
        properties = {}
        
        # Add a title based on name or id
        if "name" in entity:
            properties["Name"] = self._format_title(entity["name"])
        elif "id" in entity:
            properties["Name"] = self._format_title(f"Entity {entity['id']}")
        else:
            properties["Name"] = self._format_title("Unknown Entity")
        
        # Add other common fields
        if "date" in entity and entity["date"]:
            properties["Date"] = self._format_date(entity["date"])
        
        if "notes" in entity and entity["notes"]:
            properties["Notes"] = self._format_rich_text(entity["notes"])
        
        # Add all other properties as rich text
        for key, value in entity.items():
            if key not in ["name", "id", "date", "notes"] and isinstance(value, str):
                # Convert snake_case to Title Case for property names
                property_name = " ".join(word.capitalize() for word in key.split("_"))
                properties[property_name] = self._format_rich_text(value)
        
        return properties
    
    def _get_doctor_name(self, doctor: Dict[str, Any]) -> str:
        """
        Get a formatted doctor name.
        
        Args:
            doctor: Doctor entity
            
        Returns:
            Formatted doctor name
        """
        # Check if we already have a full name
        if "name" in doctor and doctor["name"]:
            return doctor["name"]
        
        # Otherwise build from parts
        prefix = doctor.get("prefix", "Dr.")
        first_name = doctor.get("first_name", "")
        last_name = doctor.get("last_name", "")
        
        if first_name or last_name:
            parts = [prefix, first_name, last_name]
            return " ".join(part for part in parts if part)
        
        # Fallback
        return "Unknown Doctor"
    
    def _format_title(self, title: str) -> Dict[str, Any]:
        """Format a title property for Notion."""
        return {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    
    def _format_rich_text(self, text: str) -> Dict[str, Any]:
        """Format a rich text property for Notion."""
        if not text:
            return {"rich_text": []}
            
        return {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": str(text)
                    }
                }
            ]
        }
    
    def _format_date(self, date_str: str) -> Dict[str, Any]:
        """Format a date property for Notion."""
        if not date_str:
            return {"date": None}
            
        # Normalize date format
        try:
            # Check if we already have an ISO date
            if re.match(r'^\d{4}-\d{2}-\d{2}', date_str):
                iso_date = date_str
            else:
                # Try to parse various date formats
                for fmt in ["%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        iso_date = dt.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                else:
                    # If no format matched, just use the original
                    iso_date = date_str
            
            return {
                "date": {
                    "start": iso_date
                }
            }
        except Exception as e:
            self.logger.error(f"Error formatting date '{date_str}': {e}")
            return {"date": None}
    
    def _format_select(self, option: str) -> Dict[str, Any]:
        """Format a select property for Notion."""
        if not option:
            return {"select": None}
            
        return {
            "select": {
                "name": option
            }
        }
    
    def _format_multi_select(self, options: List[str]) -> Dict[str, Any]:
        """Format a multi-select property for Notion."""
        if not options:
            return {"multi_select": []}
            
        return {
            "multi_select": [
                {"name": option} for option in options if option
            ]
        }
    
    def _format_relation(self, page_ids: List[str]) -> Dict[str, Any]:
        """Format a relation property for Notion."""
        if not page_ids:
            return {"relation": []}
            
        return {
            "relation": [
                {"id": page_id} for page_id in page_ids if page_id
            ]
        }
    
    def _format_number(self, number) -> Dict[str, Any]:
        """Format a number property for Notion."""
        try:
            return {"number": float(number) if number is not None else None}
        except (ValueError, TypeError):
            return {"number": None} 