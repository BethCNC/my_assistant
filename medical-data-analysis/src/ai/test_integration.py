"""
Test script for AI integration module.

This script demonstrates the AI integration capabilities with a test document.
"""

import os
import sys
from datetime import datetime
from pprint import pprint

# Add the project root to the path to allow running this directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.connection import get_db_session
from src.database.models.entity import Patient
from src.ai.model_integration import MedicalAIIntegration

def main():
    """Run the AI integration test."""
    # Use the database session as a context manager
    with get_db_session() as db_session:
        # Check if we have a test patient
        test_patient = db_session.query(Patient).filter(
            Patient.first_name == "Test",
            Patient.last_name == "Patient"
        ).first()
        
        if not test_patient:
            # Create a test patient
            test_patient = Patient(
                name="Test Patient",
                date_of_birth=datetime(1980, 1, 1),
                gender="female",
                has_eds=True,
                eds_type="hypermobile",
                has_neurodivergence=True,
                neurodivergence_type="ADHD"
            )
            db_session.add(test_patient)
            db_session.commit()
            print(f"Created test patient with ID: {test_patient.id}")
        else:
            print(f"Using existing test patient with ID: {test_patient.id}")
        
        # Store the patient ID as a string to avoid type mismatches
        patient_id = str(test_patient.id)
        
        # Create the AI integration
        ai = MedicalAIIntegration(db_session)
        
        # Test document
        test_document = """
        Dr. Jane Smith, MD
        Rheumatology Consultation Note
        Date: 2023-06-15
        
        Patient: Test Patient
        DOB: 01/01/1980
        
        Chief Complaint: Joint hypermobility, chronic pain, and fatigue
        
        History of Present Illness:
        Patient presents with a long history of joint hypermobility and chronic pain. 
        She reports multiple joint dislocations, particularly in the shoulders and fingers.
        The patient also experiences chronic fatigue and widespread musculoskeletal pain.
        
        Physical Examination:
        - Beighton score: 7/9, indicating hypermobility
        - Skin: Hyperextensible, thin, with visible veins
        - Scars: Several atrophic scars on knees and elbows
        
        Assessment:
        Patient meets the criteria for hypermobile Ehlers-Danlos Syndrome (hEDS) based on:
        1. Generalized joint hypermobility (Beighton score 7/9)
        2. Systemic manifestations of connective tissue disorder
        3. Absence of other connective tissue disorders
        
        Additionally, the patient reports symptoms consistent with ADHD, including difficulty with focus,
        time management, and organization, which is common in patients with hEDS.
        
        Plan:
        1. Physical therapy referral for joint stabilization exercises
        2. Prescribe Lyrica 75mg BID for pain management
        3. Recommend gentle cardiovascular exercise as tolerated
        4. Referral to psychiatry for ADHD assessment
        5. Follow up in 3 months
        
        Lab Results:
        - CBC: Within normal limits
        - ESR: 18 mm/hr (slightly elevated)
        - CRP: 2.3 mg/L (slightly elevated)
        - ANA: Negative
        
        Dr. Jane Smith, MD
        Rheumatology
        """
        
        # Process the test document
        print("Processing test document...")
        result = ai.process_document(
            document_text=test_document,
            document_type="clinical_note",
            document_date=datetime(2023, 6, 15),
            document_metadata={"provider": "Dr. Jane Smith", "specialty": "Rheumatology"},
            patient_id=patient_id
        )
        
        print("\nDocument processing result:")
        pprint(result)
        
        # Analyze patient history
        print("\nAnalyzing patient history...")
        history_analysis = ai.analyze_patient_history(patient_id)
        
        print("\nPatient history analysis:")
        pprint(history_analysis)
        
        # Test the question answering
        test_question = "What treatment was recommended for my joint pain?"
        print(f"\nAsking medical question: '{test_question}'")
        answer = ai.answer_medical_question(patient_id, test_question)
        
        print("\nMedical question answer:")
        pprint(answer)
        
        # Extract timeline
        print("\nExtracting medical timeline...")
        timeline = ai.extract_medical_timeline(patient_id)
        
        print("\nMedical timeline:")
        if timeline["timeline"]:
            for event in timeline["timeline"]:
                print(f"- {event['date'].strftime('%Y-%m-%d') if event['date'] else 'Unknown date'}: {event['description']}")
        else:
            print("No timeline events found")
        
        print("\nTimeline analysis:")
        pprint(timeline["analysis"])

if __name__ == "__main__":
    main() 