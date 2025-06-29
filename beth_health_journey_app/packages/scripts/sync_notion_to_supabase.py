#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion to Supabase Sync Script
------------------------------
This script syncs medical data from Notion databases to Supabase.
It handles multiple database types and ensures proper relationships are maintained.
"""

import os
import sys
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional

# Third-party imports
import dotenv
from notion_client import Client
from supabase import create_client, Client as SupabaseClient
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("notion-supabase-sync")

# Load environment variables
dotenv.load_dotenv()

# Notion API Client
notion = Client(auth=os.environ.get("NOTION_TOKEN"))

# Supabase Client
supabase: SupabaseClient = create_client(
    os.environ.get("NEXT_PUBLIC_SUPABASE_URL", ""),
    os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
)

# Database IDs
NOTION_MEDICAL_CALENDAR_DB_ID = os.environ.get("NOTION_MEDICAL_CALENDAR_DATABASE_ID")
NOTION_SYMPTOMS_DB_ID = os.environ.get("NOTION_SYMPTOMS_DATABASE_ID")
NOTION_MEDICAL_TEAM_DB_ID = os.environ.get("NOTION_MEDICAL_TEAM_DATABASE_ID")
NOTION_MEDICATIONS_DB_ID = os.environ.get("NOTION_MEDICATIONS_DATABASE_ID")
NOTION_HEALTH_PAGES_DB_ID = os.environ.get("NOTION_HEALTH_PAGES_DATABASE_ID")


def validate_env_vars() -> bool:
    """Validate that all required environment variables are set."""
    required_vars = [
        "NOTION_TOKEN",
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
        "NOTION_MEDICAL_CALENDAR_DATABASE_ID",
        "NOTION_SYMPTOMS_DATABASE_ID",
        "NOTION_MEDICAL_TEAM_DATABASE_ID",
        "NOTION_MEDICATIONS_DATABASE_ID",
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def query_notion_database(database_id: str) -> List[Dict[str, Any]]:
    """Query a Notion database and return all results."""
    results = []
    has_more = True
    start_cursor = None
    
    while has_more:
        response = notion.databases.query(
            database_id=database_id,
            start_cursor=start_cursor
        )
        results.extend(response["results"])
        has_more = response["has_more"]
        if has_more:
            start_cursor = response["next_cursor"]
    
    return results


def extract_notion_property(page: Dict[str, Any], property_name: str) -> Any:
    """Extract and format a property value from a Notion page."""
    prop = page["properties"].get(property_name)
    
    if not prop:
        return None
    
    prop_type = prop["type"]
    
    if prop_type == "title":
        return prop["title"][0]["plain_text"] if prop["title"] else None
    elif prop_type == "rich_text":
        return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else None
    elif prop_type == "number":
        return prop["number"]
    elif prop_type == "select":
        return prop["select"]["name"] if prop["select"] else None
    elif prop_type == "multi_select":
        return [item["name"] for item in prop["multi_select"]]
    elif prop_type == "date":
        if prop["date"]:
            return prop["date"]["start"]
        return None
    elif prop_type == "checkbox":
        return prop["checkbox"]
    elif prop_type == "relation":
        return [item["id"] for item in prop["relation"]]
    elif prop_type == "url":
        return prop["url"]
    elif prop_type == "email":
        return prop["email"]
    elif prop_type == "phone_number":
        return prop["phone_number"]
    
    return None


def sync_medical_team() -> Dict[str, str]:
    """Sync the medical team database and return a mapping of Notion IDs to Supabase IDs."""
    logger.info("Syncing medical team data...")
    notion_to_supabase_id_map = {}
    
    providers_data = query_notion_database(NOTION_MEDICAL_TEAM_DB_ID)
    
    for provider in providers_data:
        notion_id = provider["id"]
        name = extract_notion_property(provider, "Name")
        specialty = extract_notion_property(provider, "Specialty")
        facility = extract_notion_property(provider, "Facility")
        address = extract_notion_property(provider, "Address")
        phone = extract_notion_property(provider, "Phone")
        email = extract_notion_property(provider, "Email")
        website = extract_notion_property(provider, "Website")
        notes = extract_notion_property(provider, "Notes")
        
        if not name:
            logger.warning(f"Provider missing name, skipping: {notion_id}")
            continue
        
        # Check if provider already exists
        supabase_query = supabase.table("providers").select("id").eq("notion_id", notion_id)
        existing_provider = supabase_query.execute()
        
        provider_data = {
            "name": name,
            "specialty": specialty,
            "facility": facility,
            "address": address,
            "phone": phone,
            "email": email,
            "website": website,
            "notes": notes,
            "notion_id": notion_id,
            "updated_at": datetime.now().isoformat()
        }
        
        if existing_provider.data:
            # Update existing provider
            supabase_id = existing_provider.data[0]["id"]
            supabase.table("providers").update(provider_data).eq("id", supabase_id).execute()
        else:
            # Insert new provider
            provider_data["created_at"] = datetime.now().isoformat()
            result = supabase.table("providers").insert(provider_data).execute()
            supabase_id = result.data[0]["id"] if result.data else None
        
        if supabase_id:
            notion_to_supabase_id_map[notion_id] = supabase_id
    
    logger.info(f"Synced {len(notion_to_supabase_id_map)} medical providers")
    return notion_to_supabase_id_map


def sync_symptoms(provider_map: Dict[str, str]) -> Dict[str, str]:
    """Sync the symptoms database and return a mapping of Notion IDs to Supabase IDs."""
    logger.info("Syncing symptoms data...")
    notion_to_supabase_id_map = {}
    
    symptoms_data = query_notion_database(NOTION_SYMPTOMS_DB_ID)
    
    for symptom in symptoms_data:
        notion_id = symptom["id"]
        name = extract_notion_property(symptom, "Name")
        description = extract_notion_property(symptom, "Description")
        severity = extract_notion_property(symptom, "Severity")
        frequency = extract_notion_property(symptom, "Frequency")
        duration = extract_notion_property(symptom, "Duration")
        triggers = extract_notion_property(symptom, "Triggers")
        alleviating_factors = extract_notion_property(symptom, "Alleviating Factors")
        date_recorded = extract_notion_property(symptom, "Date First Recorded")
        
        if not name:
            logger.warning(f"Symptom missing name, skipping: {notion_id}")
            continue
        
        # Check if symptom already exists
        supabase_query = supabase.table("symptoms").select("id").eq("notion_id", notion_id)
        existing_symptom = supabase_query.execute()
        
        symptom_data = {
            "name": name,
            "description": description,
            "severity": severity or 5,  # Default to middle severity if none provided
            "frequency": frequency,
            "duration": duration,
            "triggers": triggers if isinstance(triggers, list) else [],
            "alleviating_factors": alleviating_factors if isinstance(alleviating_factors, list) else [],
            "date_recorded": date_recorded or datetime.now().isoformat(),
            "notion_id": notion_id,
            "updated_at": datetime.now().isoformat()
        }
        
        if existing_symptom.data:
            # Update existing symptom
            supabase_id = existing_symptom.data[0]["id"]
            supabase.table("symptoms").update(symptom_data).eq("id", supabase_id).execute()
        else:
            # Insert new symptom
            symptom_data["created_at"] = datetime.now().isoformat()
            result = supabase.table("symptoms").insert(symptom_data).execute()
            supabase_id = result.data[0]["id"] if result.data else None
        
        if supabase_id:
            notion_to_supabase_id_map[notion_id] = supabase_id
    
    logger.info(f"Synced {len(notion_to_supabase_id_map)} symptoms")
    return notion_to_supabase_id_map


def sync_medications(provider_map: Dict[str, str]) -> Dict[str, str]:
    """Sync the medications database and return a mapping of Notion IDs to Supabase IDs."""
    logger.info("Syncing medications data...")
    notion_to_supabase_id_map = {}
    
    medications_data = query_notion_database(NOTION_MEDICATIONS_DB_ID)
    
    for medication in medications_data:
        notion_id = medication["id"]
        name = extract_notion_property(medication, "Name")
        type_value = extract_notion_property(medication, "Type")
        description = extract_notion_property(medication, "Description")
        start_date = extract_notion_property(medication, "Start Date")
        end_date = extract_notion_property(medication, "End Date")
        dosage = extract_notion_property(medication, "Dosage")
        frequency = extract_notion_property(medication, "Frequency")
        effectiveness = extract_notion_property(medication, "Effectiveness")
        side_effects = extract_notion_property(medication, "Side Effects")
        prescribed_by_notion_id = extract_notion_property(medication, "Prescribed By")
        
        if not name:
            logger.warning(f"Medication missing name, skipping: {notion_id}")
            continue
        
        # Map the Notion provider ID to Supabase ID
        prescribed_by = None
        if prescribed_by_notion_id and len(prescribed_by_notion_id) > 0:
            prescribed_by = provider_map.get(prescribed_by_notion_id[0])
        
        # Check if medication already exists
        supabase_query = supabase.table("treatments").select("id").eq("notion_id", notion_id)
        existing_medication = supabase_query.execute()
        
        medication_data = {
            "name": name,
            "type": type_value or "medication",
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "dosage": dosage,
            "frequency": frequency,
            "effectiveness": effectiveness or 5,  # Default to middle effectiveness if none provided
            "side_effects": side_effects,
            "prescribed_by": prescribed_by,
            "notion_id": notion_id,
            "updated_at": datetime.now().isoformat()
        }
        
        if existing_medication.data:
            # Update existing medication
            supabase_id = existing_medication.data[0]["id"]
            supabase.table("treatments").update(medication_data).eq("id", supabase_id).execute()
        else:
            # Insert new medication
            medication_data["created_at"] = datetime.now().isoformat()
            result = supabase.table("treatments").insert(medication_data).execute()
            supabase_id = result.data[0]["id"] if result.data else None
        
        if supabase_id:
            notion_to_supabase_id_map[notion_id] = supabase_id
    
    logger.info(f"Synced {len(notion_to_supabase_id_map)} medications")
    return notion_to_supabase_id_map


def sync_medical_events(
    provider_map: Dict[str, str],
    symptom_map: Dict[str, str],
    medication_map: Dict[str, str]
) -> None:
    """Sync the medical calendar events."""
    logger.info("Syncing medical calendar events...")
    event_count = 0
    
    medical_events = query_notion_database(NOTION_MEDICAL_CALENDAR_DB_ID)
    
    for event in medical_events:
        notion_id = event["id"]
        title = extract_notion_property(event, "Name")
        description = extract_notion_property(event, "Notes")
        event_type = extract_notion_property(event, "Type")
        date = extract_notion_property(event, "Date")
        location = extract_notion_property(event, "Location")
        provider_notion_ids = extract_notion_property(event, "Doctor")
        symptom_notion_ids = extract_notion_property(event, "Linked Symptoms")
        medication_notion_ids = extract_notion_property(event, "Medications")
        
        if not title or not date:
            logger.warning(f"Medical event missing title or date, skipping: {notion_id}")
            continue
        
        # Map Notion IDs to Supabase IDs
        provider_id = None
        if provider_notion_ids and len(provider_notion_ids) > 0:
            provider_id = provider_map.get(provider_notion_ids[0])
        
        # Check if event already exists
        supabase_query = supabase.table("medical_events").select("id").eq("notion_id", notion_id)
        existing_event = supabase_query.execute()
        
        event_data = {
            "title": title,
            "description": description,
            "event_type": map_event_type(event_type),
            "date": date,
            "location": location,
            "provider_id": provider_id,
            "notion_id": notion_id,
            "updated_at": datetime.now().isoformat()
        }
        
        if existing_event.data:
            # Update existing event
            supabase_id = existing_event.data[0]["id"]
            supabase.table("medical_events").update(event_data).eq("id", supabase_id).execute()
        else:
            # Insert new event
            event_data["created_at"] = datetime.now().isoformat()
            result = supabase.table("medical_events").insert(event_data).execute()
            supabase_id = result.data[0]["id"] if result.data else None
        
        # Handle related entities (symptoms and medications) through junction tables
        if supabase_id:
            event_count += 1
            
            # Sync event symptoms
            if symptom_notion_ids:
                # First clear existing relationships
                supabase.table("event_symptoms").delete().eq("event_id", supabase_id).execute()
                
                # Add new relationships
                for symptom_notion_id in symptom_notion_ids:
                    symptom_id = symptom_map.get(symptom_notion_id)
                    if symptom_id:
                        supabase.table("event_symptoms").insert({
                            "event_id": supabase_id,
                            "symptom_id": symptom_id,
                            "created_at": datetime.now().isoformat()
                        }).execute()
            
            # Sync event medications
            if medication_notion_ids:
                # First clear existing relationships
                supabase.table("event_treatments").delete().eq("event_id", supabase_id).execute()
                
                # Add new relationships
                for medication_notion_id in medication_notion_ids:
                    treatment_id = medication_map.get(medication_notion_id)
                    if treatment_id:
                        supabase.table("event_treatments").insert({
                            "event_id": supabase_id,
                            "treatment_id": treatment_id,
                            "created_at": datetime.now().isoformat()
                        }).execute()
    
    logger.info(f"Synced {event_count} medical events")


def map_event_type(notion_event_type: Optional[str]) -> str:
    """Map Notion event types to Supabase event types."""
    if not notion_event_type:
        return "appointment"
    
    mapping = {
        "Doctor's Notes - Appt Notes": "appointment",
        "Lab Result": "test",
        "Surgery": "procedure",
        "Hospitalization": "hospitalization",
        "ER Visit": "hospitalization",
        "Urgent Care": "appointment",
        "Phone Call": "other",
        "Referral": "other",
        "Therapy": "appointment",
        "Prescription": "other"
    }
    
    return mapping.get(notion_event_type, "other")


def main():
    """Main function to sync all data from Notion to Supabase."""
    logger.info("Starting Notion to Supabase sync...")
    
    if not validate_env_vars():
        logger.error("Environment variables not properly set. Exiting.")
        sys.exit(1)
    
    try:
        # Check Supabase connection
        version = supabase.table("providers").select("id").limit(1).execute()
        logger.info("Supabase connection successful")
        
        # Execute sync process
        provider_map = sync_medical_team()
        symptom_map = sync_symptoms(provider_map)
        medication_map = sync_medications(provider_map)
        sync_medical_events(provider_map, symptom_map, medication_map)
        
        logger.info("Sync completed successfully")
    
    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise
    

if __name__ == "__main__":
    main() 