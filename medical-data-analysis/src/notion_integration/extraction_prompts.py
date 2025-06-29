"""
Extraction Prompts

This module defines prompt templates for extracting different types of medical entities.
"""

# Base prompt for medical document analysis
BASE_MEDICAL_DOCUMENT_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document content
and extract structured information as JSON.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all relevant medical entities from this document and format them as JSON.
Include appointments, medications, diagnoses, symptoms, and healthcare providers.
For each entity, include as much relevant information as possible, such as dates,
dosages, durations, severity, relationship to other entities, etc.

Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Appointment extraction prompt
APPOINTMENT_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all appointments mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all appointments mentioned in this document. Include past appointments,
current appointments being documented, and any scheduled future appointments.

For each appointment, extract:
- date (YYYY-MM-DD format if possible)
- time (if mentioned)
- doctor/provider name
- specialty
- location/facility
- purpose (if mentioned)
- notes or summary
- status (e.g., "Scheduled", "Completed", "Cancelled")

Format your response as a JSON array of appointment objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Medication extraction prompt
MEDICATION_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all medications mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all medications mentioned in this document. Include current medications,
discontinued medications, and newly prescribed medications.

For each medication, extract:
- name (use the most specific name mentioned)
- dosage (amount and unit, e.g., "10mg")
- frequency (e.g., "twice daily", "every 8 hours")
- start_date (YYYY-MM-DD format if mentioned)
- end_date (YYYY-MM-DD format if mentioned or if medication was discontinued)
- prescribing doctor (if mentioned)
- purpose/condition being treated (if mentioned)
- notes (any additional information)
- status (e.g., "Active", "Discontinued", "New prescription")

Format your response as a JSON array of medication objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Diagnosis extraction prompt
DIAGNOSIS_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all diagnoses/conditions mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all medical conditions, diagnoses, or disorders mentioned in this document.
Include confirmed diagnoses, suspected/possible diagnoses, and differential diagnoses.

For each diagnosis, extract:
- name (the specific condition name)
- status (e.g., "Confirmed", "Suspected", "Historical", "Ruled out")
- date (diagnosis date in YYYY-MM-DD format if mentioned)
- diagnosing doctor (if mentioned)
- symptoms related to this condition (if mentioned)
- treatments related to this condition (if mentioned)
- notes (any additional information)
- severity (if mentioned)

Format your response as a JSON array of diagnosis objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Symptom extraction prompt
SYMPTOM_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all symptoms mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all symptoms mentioned in this document, including chief complaints,
reported symptoms, and clinical observations.

For each symptom, extract:
- name (the specific symptom name)
- onset_date (when the symptom began, in YYYY-MM-DD format if mentioned)
- duration (how long the symptom has persisted, if mentioned)
- severity (e.g., "Mild", "Moderate", "Severe", or any scale mentioned)
- frequency (how often it occurs, if mentioned)
- location (body location, if applicable)
- related_condition (any associated diagnosis, if mentioned)
- notes (any additional information)
- status (e.g., "Current", "Resolved", "Improving", "Worsening")

Format your response as a JSON array of symptom objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Doctor extraction prompt
DOCTOR_EXTRACTION_PROMPT = """
You are a medical data extraction expert. Analyze the following medical document
and extract all healthcare providers/doctors mentioned.

DOCUMENT CONTENT:
{document_content}

DOCUMENT DATE: {document_date}
DOCUMENT TYPE: {document_type}

Extract all healthcare providers (doctors, specialists, nurses, etc.) mentioned in this document.

For each provider, extract:
- name (full name if available, or last name with title)
- specialty (area of medicine/expertise)
- facility/practice (hospital, clinic, or practice name if mentioned)
- contact information (phone, email, address if mentioned)
- role (e.g., "Primary Care Physician", "Specialist", "Consulting Physician")
- notes (any additional information)
- id (create a simple identifier based on name and specialty, e.g., "doc_smith_cardio")

Format your response as a JSON array of provider objects with these fields.
Return only valid JSON with no additional text, code blocks, or markdown.
"""

# Prompt for general entity extraction
ENTITY_EXTRACTION_PROMPT = """
You are a medical data extraction assistant specializing in identifying medical entities from clinical documents and patient narratives.

Carefully analyze the following medical text and extract these entities:

1. Doctors/Providers: Names and specialties
2. Appointments: Dates, doctors, locations, and purposes
3. Medications: Names, dosages, frequencies, and purposes
4. Conditions/Diagnoses: Names, dates diagnosed, and status
5. Symptoms: Descriptions, severity, locations, and durations
6. Lab Results: Test names, values, reference ranges, and dates
7. Procedures: Names, dates, locations, and purposes

For each entity, provide structured information with as much detail as available in the text.
Focus specifically on hypermobility conditions, connective tissue disorders, neurodevelopmental conditions, and chronic pain patterns.

Medical Text:
{text}

Response should be in JSON format with these keys:
- doctors: [{"name": "", "specialty": "", ...}]
- appointments: [{"date": "", "doctor_name": "", "purpose": "", ...}]
- medications: [{"name": "", "dosage": "", "frequency": "", ...}]
- conditions: [{"name": "", "date_diagnosed": "", "status": "", ...}]
- symptoms: [{"name": "", "severity": "", "location": "", ...}]
- lab_results: [{"test_name": "", "value": "", "reference_range": "", ...}]
- procedures: [{"name": "", "date": "", "location": "", ...}]
"""

# Specialized prompt for hypermobility/EDS extraction
EDS_EXTRACTION_PROMPT = """
You are a medical data extraction assistant specializing in hypermobility spectrum disorders and Ehlers-Danlos Syndrome (EDS).

Carefully analyze the following medical text and extract information related to hypermobility, connective tissue disorders, and related symptoms.

Pay special attention to:
1. Beighton Score measurements
2. Joint hypermobility descriptions
3. Skin hyperextensibility or abnormalities
4. Marfanoid features
5. Tissue fragility or poor wound healing
6. Joint subluxations or dislocations
7. Chronic musculoskeletal pain
8. Autonomic symptoms (POTS, dysautonomia)
9. Mast cell symptoms (MCAS)
10. Gastrointestinal symptoms
11. Diagnoses or evaluations for EDS subtypes
12. Family history of hypermobility disorders

Medical Text:
{text}

Response should be in JSON format with these keys:
- hypermobility_metrics: {"beighton_score": "", "affected_joints": [], ...}
- eds_criteria: {"skin_findings": [], "tissue_fragility": [], ...}
- comorbidities: [{"name": "", "relation_to_eds": "", ...}]
- symptoms: [{"name": "", "severity": "", "location": "", ...}]
- treatments: [{"name": "", "effectiveness": "", ...}]
"""

# Specialized prompt for neurodevelopmental condition extraction
NEURODEVELOPMENTAL_EXTRACTION_PROMPT = """
You are a medical data extraction assistant specializing in neurodevelopmental conditions like ASD (Autism Spectrum Disorder) and ADHD.

Carefully analyze the following medical text and extract information related to neurodevelopmental conditions and symptoms.

Pay special attention to:
1. Social communication patterns
2. Restricted or repetitive behaviors
3. Sensory processing issues
4. Executive function challenges
5. Attention and focus descriptions
6. Developmental milestones
7. Formal assessments or screening tools used
8. Diagnoses of ASD, ADHD, or other neurodevelopmental conditions
9. Accommodations or supports mentioned
10. Impact on daily functioning
11. Co-occurring conditions (anxiety, depression, etc.)
12. Treatment approaches or therapies

Medical Text:
{text}

Response should be in JSON format with these keys:
- diagnoses: [{"name": "", "date_diagnosed": "", "assessing_provider": "", ...}]
- assessment_metrics: {"tools_used": [], "key_findings": [], ...}
- symptom_patterns: {"social": [], "behavioral": [], "sensory": [], "executive": [], ...}
- supports: [{"type": "", "effectiveness": "", ...}]
- treatments: [{"name": "", "effectiveness": "", ...}]
"""

# Specialized prompt for symptom analysis
SYMPTOM_ANALYSIS_PROMPT = """
You are a medical data extraction assistant specializing in symptom analysis and pattern recognition.

Carefully analyze the following medical text and extract detailed information about symptoms, their patterns, and potential relationships.

Pay special attention to:
1. Symptom descriptions and characteristics
2. Severity and frequency patterns
3. Triggers and alleviating factors
4. Symptom progression over time
5. Relationships between symptoms
6. Impact on functioning and quality of life
7. Correlation with medications or treatments
8. Patterns related to specific conditions
9. Environmental or situational factors
10. Cyclical or chronological patterns

Medical Text:
{text}

Response should be in JSON format with these keys:
- primary_symptoms: [{"name": "", "characteristics": [], "severity_pattern": "", ...}]
- symptom_clusters: [{"related_symptoms": [], "potential_mechanism": "", ...}]
- triggers: [{"trigger": "", "associated_symptoms": [], ...}]
- relieving_factors: [{"factor": "", "effectiveness": "", ...}]
- temporal_patterns: {"daily_patterns": [], "monthly_patterns": [], "progressive_changes": [], ...}
- functional_impact: {"domains_affected": [], "severity": "", ...}
"""

from langchain.prompts import PromptTemplate
from typing import Dict

# Main extraction prompt for general medical documents
GENERAL_EXTRACTION_PROMPT = """
You are a medical entity extraction specialist tasked with analyzing medical documents.
Extract structured information from the following medical text.

Focus on identifying the following entity types:
1. APPOINTMENTS: Medical appointments, visits, or procedures with dates, providers, and reasons
2. MEDICATIONS: Prescribed medications with dosages, frequencies, and purposes
3. DIAGNOSES: Medical conditions, diagnoses, or disorders mentioned
4. SYMPTOMS: Symptoms, complaints, or health issues described
5. DOCTORS: Healthcare providers mentioned with their specialties if available

For each entity, extract as many details as possible, including:
- Names, descriptions, dates, and relationships between entities
- Severity levels, durations, and frequency of symptoms
- Dosage information, start/end dates for medications
- Specialty information for healthcare providers
- Dates of diagnosis for conditions
- Status information (active, resolved, etc.)

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
{
  "appointments": [
    {
      "title": "Appointment description",
      "date": "YYYY-MM-DD",
      "provider": "Provider name",
      "specialty": "Medical specialty",
      "notes": "Additional information",
      "status": "completed/scheduled/cancelled",
      "location": "Facility or clinic name"
    }
  ],
  "medications": [
    {
      "name": "Medication name",
      "dosage": "Dosage information",
      "frequency": "How often taken",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD or null if ongoing",
      "prescribed_by": "Prescriber name",
      "purpose": "Reason for medication",
      "notes": "Additional information"
    }
  ],
  "diagnoses": [
    {
      "name": "Condition name",
      "date_diagnosed": "YYYY-MM-DD",
      "diagnosed_by": "Provider name",
      "status": "active/resolved/etc",
      "notes": "Additional information",
      "related_symptoms": ["symptom1", "symptom2"]
    }
  ],
  "symptoms": [
    {
      "name": "Symptom description",
      "first_reported": "YYYY-MM-DD",
      "severity": "mild/moderate/severe",
      "frequency": "constant/intermittent/etc",
      "duration": "Duration information",
      "related_condition": "Associated diagnosis if mentioned",
      "notes": "Additional details"
    }
  ],
  "doctors": [
    {
      "name": "Provider name",
      "specialty": "Medical specialty",
      "facility": "Hospital/practice name",
      "contact": "Contact information if available",
      "notes": "Additional information"
    }
  ]
}

IMPORTANT RULES:
1. Extract ONLY information present in the text - do not infer or make up details
2. Use null for missing values, don't guess information not present in the text
3. Include partial information even if all fields aren't available
4. Format dates as YYYY-MM-DD when possible
5. If date is mentioned but incomplete, use the provided document date as context
6. Use proper medical terminology and preserve the exact medication dosages, diagnoses, etc.
7. Pay special attention to temporal information and relationships between entities
8. Look for EDS (Ehlers-Danlos Syndrome), POTS, MCAS, and autism spectrum related information
9. Capture both current and historical medical information

Document Type: {document_type}
Document Date: {document_date}

TEXT:
{text}
"""

# Specialized prompt for clinical notes
CLINICAL_NOTE_PROMPT = """
You are a medical entity extraction specialist tasked with analyzing a clinical note.
Extract structured information from the following clinical note, which typically contains a provider's
detailed assessment, plan, and observations from a medical appointment.

Focus on identifying the following entity types:
1. APPOINTMENTS: Details about this visit and any scheduled follow-ups
2. MEDICATIONS: All medications mentioned - current, new prescriptions, discontinued, or adjusted
3. DIAGNOSES: All conditions discussed - new, confirmed, ruled out, or ongoing
4. SYMPTOMS: All symptoms reported by the patient or observed by the provider
5. DOCTORS: The authoring provider and any other providers mentioned or referrals made

For each entity, extract as many details as possible, including:
- Names, descriptions, dates, and relationships between entities
- Severity levels, durations, and frequency of symptoms
- Dosage information, start/end dates for medications
- Specialty information for healthcare providers
- Dates of diagnosis for conditions
- Status information (active, resolved, etc.)
- Pay special attention to the assessment and plan sections

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
{
  "appointments": [
    {
      "title": "Appointment description",
      "date": "YYYY-MM-DD",
      "provider": "Provider name",
      "specialty": "Medical specialty",
      "notes": "Additional information",
      "status": "completed/scheduled/cancelled",
      "location": "Facility or clinic name",
      "follow_up": "Follow-up instructions"
    }
  ],
  "medications": [
    {
      "name": "Medication name",
      "dosage": "Dosage information",
      "frequency": "How often taken",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD or null if ongoing",
      "prescribed_by": "Prescriber name",
      "purpose": "Reason for medication",
      "notes": "Additional information",
      "status": "new/continued/discontinued/adjusted"
    }
  ],
  "diagnoses": [
    {
      "name": "Condition name",
      "date_diagnosed": "YYYY-MM-DD",
      "diagnosed_by": "Provider name",
      "status": "active/resolved/etc",
      "notes": "Additional information",
      "related_symptoms": ["symptom1", "symptom2"],
      "plan": "Treatment plan for this condition"
    }
  ],
  "symptoms": [
    {
      "name": "Symptom description",
      "first_reported": "YYYY-MM-DD",
      "severity": "mild/moderate/severe",
      "frequency": "constant/intermittent/etc",
      "duration": "Duration information",
      "related_condition": "Associated diagnosis if mentioned",
      "notes": "Additional details"
    }
  ],
  "doctors": [
    {
      "name": "Provider name",
      "specialty": "Medical specialty",
      "facility": "Hospital/practice name",
      "contact": "Contact information if available",
      "notes": "Additional information"
    }
  ]
}

IMPORTANT RULES:
1. Extract ONLY information present in the text - do not infer or make up details
2. Use null for missing values, don't guess information not present in the text
3. Include partial information even if all fields aren't available
4. Format dates as YYYY-MM-DD when possible
5. If date is mentioned but incomplete, use the provided document date as context
6. Use proper medical terminology and preserve the exact medication dosages, diagnoses, etc.
7. In clinical notes, pay special attention to the Assessment and Plan sections
8. Look for EDS (Ehlers-Danlos Syndrome), POTS, MCAS, and autism spectrum related information
9. Record assessment findings and recommendations accurately

Document Type: Clinical Note
Document Date: {document_date}

TEXT:
{text}
"""

# Specialized prompt for lab results
LAB_RESULT_PROMPT = """
You are a medical entity extraction specialist tasked with analyzing a lab result document.
Extract structured information from the following lab or test results.

For lab results, focus on:
1. APPOINTMENTS: The appointment or visit when this test was ordered/performed
2. DOCTORS: The ordering provider and any other providers mentioned
3. DIAGNOSES: Any conditions mentioned as reason for testing or in the interpretation
4. SYMPTOMS: Any symptoms mentioned as reason for testing

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
{
  "appointments": [
    {
      "title": "Lab test/procedure",
      "date": "YYYY-MM-DD",
      "provider": "Ordering provider",
      "specialty": "Medical specialty",
      "notes": "Test details",
      "status": "completed/pending",
      "location": "Testing facility"
    }
  ],
  "diagnoses": [
    {
      "name": "Condition name",
      "status": "confirmed/suspected/ruled out",
      "notes": "Relation to test results"
    }
  ],
  "symptoms": [
    {
      "name": "Symptom description",
      "notes": "Relation to test results"
    }
  ],
  "doctors": [
    {
      "name": "Provider name",
      "specialty": "Medical specialty",
      "role": "ordering/interpreting/reviewing",
      "facility": "Hospital/lab name"
    }
  ],
  "test_results": [
    {
      "test_name": "Name of test",
      "result": "Result value",
      "units": "Measurement units",
      "reference_range": "Normal range",
      "interpretation": "Normal/Abnormal/Borderline",
      "notes": "Additional information"
    }
  ]
}

IMPORTANT RULES:
1. Extract ONLY information present in the text - do not infer or make up details
2. Use null for missing values, don't guess information not present in the text
3. Be precise with test names, values, and reference ranges
4. Pay special attention to abnormal results and clinical interpretations
5. Include notes about what the results might indicate if mentioned
6. Format dates as YYYY-MM-DD when possible
7. If date is mentioned but incomplete, use the provided document date as context

Document Type: Lab Result
Document Date: {document_date}

TEXT:
{text}
"""

# Specialized prompt for radiology reports
RADIOLOGY_REPORT_PROMPT = """
You are a medical entity extraction specialist tasked with analyzing a radiology or imaging report.
Extract structured information from the following imaging report.

For imaging reports, focus on:
1. APPOINTMENTS: The imaging procedure itself
2. DOCTORS: The ordering provider and the radiologist/interpreter
3. DIAGNOSES: Any conditions mentioned as reason for imaging or in the findings
4. SYMPTOMS: Any symptoms mentioned as reason for imaging or in the findings

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
{
  "appointments": [
    {
      "title": "Imaging procedure",
      "date": "YYYY-MM-DD",
      "provider": "Ordering provider",
      "notes": "Procedure details",
      "status": "completed",
      "location": "Imaging facility"
    }
  ],
  "diagnoses": [
    {
      "name": "Condition name",
      "status": "confirmed/suspected/ruled out",
      "notes": "Relation to imaging findings"
    }
  ],
  "symptoms": [
    {
      "name": "Symptom description",
      "notes": "Relation to imaging findings"
    }
  ],
  "doctors": [
    {
      "name": "Provider name",
      "specialty": "Medical specialty",
      "role": "ordering/interpreting",
      "facility": "Hospital/imaging center name"
    }
  ],
  "imaging_results": {
    "procedure": "Type of imaging",
    "area": "Body area imaged",
    "findings": "Detailed findings",
    "impression": "Radiologist's impression",
    "comparison": "Comparison to prior studies if mentioned",
    "recommendations": "Follow-up recommendations if any"
  }
}

IMPORTANT RULES:
1. Extract ONLY information present in the text - do not infer or make up details
2. Use null for missing values, don't guess information not present in the text
3. Distinguish between the findings section and impression section
4. Pay special attention to any abnormalities or significant findings
5. Include any recommended follow-up actions
6. Format dates as YYYY-MM-DD when possible
7. If date is mentioned but incomplete, use the provided document date as context

Document Type: Radiology Report
Document Date: {document_date}

TEXT:
{text}
"""

# Specialized prompt for visit summaries
VISIT_SUMMARY_PROMPT = """
You are a medical entity extraction specialist tasked with analyzing a visit summary.
Extract structured information from the following medical visit summary.

For visit summaries, focus on:
1. APPOINTMENTS: Details about this visit and any scheduled follow-ups
2. MEDICATIONS: All medications mentioned - current, new prescriptions, discontinued, or adjusted
3. DIAGNOSES: All conditions discussed - new, confirmed, ruled out, or ongoing
4. SYMPTOMS: All symptoms reported or addressed during the visit
5. DOCTORS: The provider seen and any other providers mentioned or referrals made

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
{
  "appointments": [
    {
      "title": "Visit description",
      "date": "YYYY-MM-DD",
      "provider": "Provider name",
      "specialty": "Medical specialty",
      "notes": "Visit details",
      "status": "completed",
      "location": "Facility name",
      "follow_up": "Follow-up instructions",
      "next_appointment": "YYYY-MM-DD or description of next visit"
    }
  ],
  "medications": [
    {
      "name": "Medication name",
      "dosage": "Dosage information",
      "frequency": "How often taken",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD or null if ongoing",
      "prescribed_by": "Prescriber name",
      "purpose": "Reason for medication",
      "notes": "Additional information",
      "status": "new/continued/discontinued/adjusted"
    }
  ],
  "diagnoses": [
    {
      "name": "Condition name",
      "date_diagnosed": "YYYY-MM-DD",
      "diagnosed_by": "Provider name",
      "status": "active/resolved/etc",
      "notes": "Additional information",
      "related_symptoms": ["symptom1", "symptom2"],
      "plan": "Treatment plan for this condition"
    }
  ],
  "symptoms": [
    {
      "name": "Symptom description",
      "status": "improved/unchanged/worsened",
      "severity": "mild/moderate/severe",
      "frequency": "constant/intermittent/etc",
      "related_condition": "Associated diagnosis if mentioned",
      "notes": "Additional details"
    }
  ],
  "doctors": [
    {
      "name": "Provider name",
      "specialty": "Medical specialty",
      "facility": "Hospital/practice name",
      "role": "primary/consulting/referred"
    }
  ],
  "instructions": {
    "care_instructions": "Patient care instructions",
    "lifestyle_changes": "Recommended lifestyle changes",
    "diet": "Dietary instructions",
    "activity": "Activity instructions or restrictions"
  }
}

IMPORTANT RULES:
1. Extract ONLY information present in the text - do not infer or make up details
2. Use null for missing values, don't guess information not present in the text
3. Include partial information even if all fields aren't available
4. Format dates as YYYY-MM-DD when possible
5. If date is mentioned but incomplete, use the provided document date as context
6. Carefully extract any patient instructions or follow-up details
7. Note any changes to medications or treatment plans
8. Pay special attention to EDS, POTS, MCAS, and autism spectrum related information

Document Type: Visit Summary
Document Date: {document_date}

TEXT:
{text}
"""

# Create a dictionary to map document types to specialized prompts
DOCUMENT_TYPE_PROMPTS = {
    "clinical_note": CLINICAL_NOTE_PROMPT,
    "lab_result": LAB_RESULT_PROMPT,
    "radiology_report": RADIOLOGY_REPORT_PROMPT,
    "visit_summary": VISIT_SUMMARY_PROMPT,
    # Default to general prompt if no specialized prompt exists
    "medical_document": GENERAL_EXTRACTION_PROMPT,
    "medical_report": GENERAL_EXTRACTION_PROMPT,
    "medical_letter": GENERAL_EXTRACTION_PROMPT,
    "consultation": GENERAL_EXTRACTION_PROMPT,
}

def get_extraction_prompt(document_type: str = "medical_document") -> PromptTemplate:
    """
    Get the appropriate extraction prompt template for a document type.
    
    Args:
        document_type: Type of medical document
        
    Returns:
        PromptTemplate: The prompt template for entity extraction
    """
    # Get the appropriate prompt text (default to general if not found)
    prompt_text = DOCUMENT_TYPE_PROMPTS.get(
        document_type.lower(), GENERAL_EXTRACTION_PROMPT
    )
    
    # Create and return the prompt template
    return PromptTemplate(
        template=prompt_text,
        input_variables=["text", "document_date", "document_type"]
    ) 