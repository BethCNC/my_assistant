import sys
import os
import unittest
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.extraction.text_extractor import TextExtractor
from src.processing.medical_text_processor import MedicalTextProcessor
from src.processing.factory import ProcessorFactory

class TestClinicalDataExtraction(unittest.TestCase):
    """Test the extraction and processing of clinical data with focus on providers and notes."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Create a test clinical note
        self.test_clinical_note = self.test_dir / "clinical_note_2023-09-15.txt"
        self.clinical_note_content = """
PATIENT ENCOUNTER NOTE
Date of Service: 09/15/2023
Provider: Dr. Jane Smith, Rheumatology

CHIEF COMPLAINT:
Patient presents with joint pain and fatigue.

HISTORY OF PRESENT ILLNESS:
30-year-old female with a history of hypermobility syndrome presents today with complaints of 
worsening joint pain, particularly in the fingers, wrists, and knees. Patient reports increased 
fatigue over the past 3 months. She describes the pain as "constant aching" that worsens with 
activity. She was previously seen by Dr. Mark Johnson in Neurology on 08/10/2023 for evaluation 
of possible dysautonomia.

MEDICATIONS:
1. Ibuprofen 600mg PRN for pain
2. Cymbalta 30mg daily for pain management
3. Vitamin D3 2000 IU daily

ALLERGIES:
Penicillin - hives

PAST MEDICAL HISTORY:
- Hypermobility syndrome, diagnosed 2018
- Chronic fatigue
- Irritable bowel syndrome

PHYSICAL EXAMINATION:
Vital Signs: BP 118/76, HR 82, Temp 98.6°F
General: Patient appears tired but in no acute distress.
Musculoskeletal: Generalized joint hypermobility noted with Beighton score of 7/9. Tenderness to 
palpation of multiple finger joints bilaterally. Mild synovitis of the right wrist. Bilateral knee 
hyperextension observed.

I note significant laxity in the finger joints and hyperextension of elbows beyond 10 degrees.
The patient demonstrates skin hyperextensibility and easy bruising on the extremities.

ASSESSMENT:
1. Hypermobility Spectrum Disorder with features suggestive of hEDS (hypermobile Ehlers-Danlos Syndrome)
2. Chronic pain syndrome
3. Suspected dysautonomia - will need further evaluation

PLAN:
1. Order comprehensive connective tissue panel
2. Referral to geneticist for formal hEDS evaluation
3. Continue current medications
4. Physical therapy 2x/week for joint stabilization exercises
5. Follow up in 6 weeks

Dr. Smith explained, "Your symptoms and physical examination are consistent with hypermobile 
Ehlers-Danlos Syndrome, but genetic testing is important to rule out other types of EDS."

FOLLOW-UP:
Return in 6 weeks. Call sooner if symptoms worsen.

Jane Smith, MD
Rheumatology
"""
        with open(self.test_clinical_note, 'w') as f:
            f.write(self.clinical_note_content)

    def test_provider_extraction(self):
        """Test extraction of healthcare provider names."""
        extractor = TextExtractor()
        result = extractor.process_file(self.test_clinical_note)
        
        # Check providers were extracted
        self.assertIn("providers", result)
        providers = result["providers"]
        
        # Verify at least one provider was found
        self.assertGreaterEqual(len(providers), 1)
        
        # Check if Dr. Jane Smith was identified
        provider_names = [p["name"] for p in providers]
        self.assertIn("Jane Smith", provider_names)
        
        # Check if Dr. Mark Johnson was identified
        self.assertIn("Mark Johnson", provider_names)

    def test_appointment_date_extraction(self):
        """Test extraction of appointment dates."""
        extractor = TextExtractor()
        result = extractor.process_file(self.test_clinical_note)
        
        # Check appointment dates were extracted
        self.assertIn("appointment_dates", result)
        appointment_dates = result["appointment_dates"]
        
        # Verify at least one appointment date was found
        self.assertGreaterEqual(len(appointment_dates), 1)
        
        # Check if the correct date was extracted
        date_values = [a["date"] for a in appointment_dates]
        self.assertIn("2023-09-15", date_values)

    def test_medical_text_processing(self):
        """Test processing of clinical notes with the medical text processor."""
        extractor = TextExtractor()
        extraction_result = extractor.process_file(self.test_clinical_note)
        
        # Create processor
        processor = MedicalTextProcessor()
        processed_data = processor.process(extraction_result)
        
        # Check if clinical observations were extracted
        self.assertIn("clinical_observations", processed_data)
        observations = processed_data["clinical_observations"]
        self.assertGreaterEqual(len(observations), 1)
        
        # Check if doctor's notes were extracted
        self.assertIn("doctor_notes", processed_data)
        doctor_notes = processed_data["doctor_notes"]
        self.assertGreaterEqual(len(doctor_notes), 1)
        
        # Verify extraction of at least one doctor quote
        quote_notes = [note for note in doctor_notes if note.get("type") == "quote"]
        self.assertGreaterEqual(len(quote_notes), 1)
        self.assertIn("Your symptoms and physical examination are consistent with", quote_notes[0]["note"])
        
        # Check if treatment plan was extracted
        self.assertIn("treatment_plan", processed_data)
        treatment_plan = processed_data["treatment_plan"]
        self.assertGreaterEqual(len(treatment_plan), 1)
        
        # Verify different plan types were categorized correctly
        plan_types = [item["type"] for item in treatment_plan]
        self.assertIn("testing", plan_types)
        self.assertIn("referral", plan_types)
        self.assertIn("follow_up", plan_types)

    def test_clinical_summary(self):
        """Test the creation of a clinical summary."""
        extractor = TextExtractor()
        extraction_result = extractor.process_file(self.test_clinical_note)
        
        # Create processor
        processor = MedicalTextProcessor()
        processed_data = processor.process(extraction_result)
        
        # Check if clinical summary was created
        self.assertIn("clinical_summary", processed_data)
        summary = processed_data["clinical_summary"]
        
        # Verify summary structure
        self.assertIn("appointment_info", summary)
        self.assertIn("providers", summary)
        self.assertIn("diagnoses", summary)
        self.assertIn("treatment_plan", summary)
        self.assertIn("medications", summary)
        
        # Check appointment date
        if summary["appointment_info"] and "date" in summary["appointment_info"]:
            self.assertEqual("2023-09-15", summary["appointment_info"]["date"])
        
        # Check providers
        if summary["providers"]:
            provider_names = [p["name"] for p in summary["providers"]]
            self.assertIn("Jane Smith", provider_names)
        
        # Check diagnoses
        if summary["diagnoses"]:
            diagnoses = [d["condition"] for d in summary["diagnoses"]]
            self.assertTrue(any("hypermobile" in d.lower() for d in diagnoses))

    def test_factory_creation(self):
        """Test the processor factory correctly creates a medical text processor."""
        extractor = TextExtractor()
        extraction_result = extractor.process_file(self.test_clinical_note)
        
        # Use factory to create processor
        factory = ProcessorFactory()
        
        # Based on the clinical note content, we know it should be a medical_note
        document_type = "medical_note"
        
        # Get the processor with the correct document type string
        processor = factory.get_processor(document_type)
        
        # Verify processor type
        self.assertIsInstance(processor, MedicalTextProcessor)
        
        # Process the data
        processed_data = processor.process(extraction_result)
        
        # Verify key elements were extracted
        self.assertIn("providers", processed_data)
        self.assertIn("appointment_dates", processed_data)
        self.assertIn("clinical_observations", processed_data)
        self.assertIn("doctor_notes", processed_data)

    def tearDown(self):
        """Clean up test environment."""
        if self.test_clinical_note.exists():
            self.test_clinical_note.unlink()
        
        # Remove test directory if empty
        try:
            self.test_dir.rmdir()
        except OSError:
            # Directory not empty, leave it
            pass

if __name__ == "__main__":
    unittest.main() 