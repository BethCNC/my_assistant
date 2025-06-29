#!/usr/bin/env python3
"""
Test Extraction

A simple script to test the entity extraction on the sample medical visit.
"""

import os
import json
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path to help with imports
import sys
sys.path.append(str(Path(__file__).parent))

# Import our entity extractor
from src.notion_integration.entity_extractor import EntityExtractor

def extract_key_medical_entities(data):
    """Extract key medical entities in a structured format"""
    entities = {
        "conditions": [],
        "medications": [],
        "symptoms": [],
        "providers": [],
        "appointments": []
    }
    
    # Try to extract from visit_summary
    visit = data.get("visit_summary", {})
    
    # Extract conditions
    assessment = visit.get("assessment", [])
    for item in assessment:
        if "condition" in item:
            entities["conditions"].append({
                "name": item["condition"],
                "status": item.get("status", "active"),
                "criteria": item.get("criteria", ""),
                "related_to": item.get("related_to", ""),
                "suspected_condition": item.get("suspected_condition", "")
            })
    
    # Extract medications
    medications = visit.get("medications", [])
    for med in medications:
        if "name" in med:
            entities["medications"].append({
                "name": med["name"],
                "dosage": med.get("dosage", ""),
                "frequency": med.get("frequency", ""),
                "indication": med.get("indication", "")
            })
    
    # Extract symptoms
    if "history_of_present_illness" in visit:
        symptoms = visit["history_of_present_illness"].get("symptoms", [])
        for symptom in symptoms:
            if "name" in symptom:
                entities["symptoms"].append({
                    "name": symptom["name"],
                    "locations": symptom.get("locations", []),
                    "duration": symptom.get("duration", ""),
                    "related_condition": symptom.get("related_condition", "")
                })
    
    # Extract providers
    if "provider" in visit:
        provider = visit["provider"]
        entities["providers"].append({
            "name": provider.get("name", ""),
            "specialty": provider.get("specialty", ""),
            "contact": provider.get("contact", {})
        })
    
    # Extract follow-up appointments
    follow_ups = visit.get("follow_up", [])
    for appt in follow_ups:
        entities["appointments"].append({
            "provider": appt.get("appointment_with", appt.get("consultation_with", "")),
            "specialty": appt.get("specialty", ""),
            "timeframe": appt.get("timeframe", ""),
            "purpose": appt.get("purpose", ""),
            "status": appt.get("status", "scheduled")
        })
    
    return entities

def main():
    """Test entity extraction on sample data"""
    # Load environment variables for API keys
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Missing OPENAI_API_KEY in environment variables")
        return 1
    
    # Load sample file
    sample_path = Path("data/input/sample_visit.txt")
    if not sample_path.exists():
        logger.error(f"Sample file not found: {sample_path}")
        return 1
    
    with open(sample_path, "r") as f:
        content = f.read()
    
    logger.info(f"Loaded sample file: {len(content)} characters")
    
    # Create entity extractor
    extractor = EntityExtractor(api_key=api_key)
    
    logger.info("Extracting entities from sample medical visit...")
    
    # Extract entities from the sample content
    entities = extractor.extract_entities(
        text=content,
        document_date="2023-09-15",
        document_type="Clinical Visit"
    )
    
    if not entities:
        logger.error("Failed to extract entities")
        return 1
    
    logger.info("Successfully extracted entities:")
    print(json.dumps(entities, indent=2))
    
    # Save to output file
    output_dir = Path("data/output")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with open(output_dir / "extracted_entities.json", "w") as f:
        json.dump(entities, f, indent=2)
    
    logger.info(f"Saved extracted entities to {output_dir}/extracted_entities.json")
    
    # Extract structured medical entities
    structured_entities = extract_key_medical_entities(entities)
    logger.info("Extracted structured medical entities:")
    print(json.dumps(structured_entities, indent=2))
    
    # Save structured entities
    with open(output_dir / "structured_entities.json", "w") as f:
        json.dump(structured_entities, f, indent=2)
    
    logger.info(f"Saved structured medical entities to {output_dir}/structured_entities.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 