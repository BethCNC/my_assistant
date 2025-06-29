"""
Medical Entity Extraction

This module provides functionality for extracting medical entities from text.
"""
import logging
import re
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalEntityExtractor:
    """Extracts medical entities from text using NLP models."""
    
    def __init__(self, model_name: str = "default-medical-ner"):
        """Initialize the entity extractor with a specified model.
        
        Args:
            model_name: Name of the model to use for entity extraction
        """
        self.model_name = model_name
        logger.info(f"Initializing Medical Entity Extractor with model {model_name}")
        
        # Define medical conditions and their keywords
        self.conditions = {
            "Hypertension": ["hypertension", "high blood pressure", "elevated bp", "htn"],
            "Diabetes": ["diabetes", "type 1 diabetes", "type 2 diabetes", "diabetic", "t1d", "t2d", "dm", "dm2"],
            "Asthma": ["asthma", "reactive airway", "bronchospasm"],
            "COPD": ["copd", "chronic obstructive pulmonary disease", "emphysema", "chronic bronchitis"],
            "Hyperlipidemia": ["hyperlipidemia", "high cholesterol", "elevated cholesterol", "high lipids"],
            "CAD": ["coronary artery disease", "cad", "ischemic heart disease", "coronary heart disease"],
            "Arthritis": ["arthritis", "osteoarthritis", "rheumatoid arthritis", "psoriatic arthritis"],
            "Hypothyroidism": ["hypothyroidism", "underactive thyroid", "low thyroid"],
            "Hyperthyroidism": ["hyperthyroidism", "overactive thyroid", "graves disease", "thyrotoxicosis"],
            "Depression": ["depression", "major depressive disorder", "mdd"],
            "Anxiety": ["anxiety", "generalized anxiety disorder", "gad", "panic disorder"],
            "Migraine": ["migraine", "migraine headache", "chronic migraine"],
            "GERD": ["gerd", "gastroesophageal reflux disease", "acid reflux", "reflux"],
            "IBS": ["ibs", "irritable bowel syndrome", "spastic colon"],
            "Fibromyalgia": ["fibromyalgia", "fibro", "fms"],
            "Chronic Fatigue": ["chronic fatigue", "cfs", "myalgic encephalomyelitis", "me/cfs"],
            "Osteoporosis": ["osteoporosis", "osteopenia", "bone density loss"],
            "Anemia": ["anemia", "iron deficiency", "low hemoglobin", "low hgb"],
            "EDS": ["ehlers-danlos syndrome", "eds", "hypermobility syndrome", "hms", "joint hypermobility", "hsd"],
            "POTS": ["postural orthostatic tachycardia syndrome", "pots", "orthostatic intolerance", "oi"],
            "MCAS": ["mast cell activation syndrome", "mcas", "mast cell disorder", "mastocytosis"]
        }
        
        # Define common medications
        self.medications = {
            "Antihypertensives": ["lisinopril", "metoprolol", "amlodipine", "losartan", "hydrochlorothiazide", "hctz", "atenolol", "valsartan"],
            "Antidiabetics": ["metformin", "glipizide", "glyburide", "insulin", "jardiance", "ozempic", "trulicity", "victoza", "januvia"],
            "Statins": ["atorvastatin", "lipitor", "simvastatin", "zocor", "rosuvastatin", "crestor", "pravastatin", "lovastatin"],
            "Antidepressants": ["sertraline", "zoloft", "fluoxetine", "prozac", "escitalopram", "lexapro", "bupropion", "wellbutrin", "venlafaxine", "effexor"],
            "Anxiolytics": ["alprazolam", "xanax", "lorazepam", "ativan", "diazepam", "valium", "clonazepam", "klonopin"],
            "Pain": ["acetaminophen", "tylenol", "ibuprofen", "advil", "motrin", "naproxen", "aleve", "tramadol", "hydrocodone", "oxycodone"],
            "Thyroid": ["levothyroxine", "synthroid", "armour thyroid", "liothyronine", "cytomel"],
            "Antihistamines": ["loratadine", "claritin", "cetirizine", "zyrtec", "fexofenadine", "allegra", "diphenhydramine", "benadryl"],
            "GERD": ["omeprazole", "prilosec", "pantoprazole", "protonix", "famotidine", "pepcid", "ranitidine", "zantac"],
            "Corticosteroids": ["prednisone", "prednisolone", "methylprednisolone", "medrol", "dexamethasone", "fluticasone"],
            "Bronchodilators": ["albuterol", "ventolin", "proair", "salmeterol", "advair", "symbicort", "spiriva"],
            "ADHD": ["methylphenidate", "ritalin", "concerta", "amphetamine", "adderall", "vyvanse", "strattera"],
            "Anticonvulsants": ["gabapentin", "neurontin", "pregabalin", "lyrica", "lamotrigine", "lamictal", "levetiracetam", "keppra"],
            "Antimigraine": ["sumatriptan", "imitrex", "rizatriptan", "maxalt", "topiramate", "topamax"]
        }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract medical entities from text.
        
        Args:
            text: Medical text to extract entities from
            
        Returns:
            Dictionary containing extracted entities by type
        """
        logger.info(f"Extracting entities from text ({len(text)} chars)")
        
        # Extract various entity types
        entities = {
            "conditions": self._extract_conditions(text),
            "medications": self._extract_medications(text),
            "procedures": self._extract_procedures(text),
            "lab_results": self._extract_lab_results(text),
            "vital_signs": self._extract_vital_signs(text)
        }
        
        return entities
    
    def extract_specialty(self, text: str) -> Optional[str]:
        """Extract medical specialty from text.
        
        Args:
            text: Medical text to extract specialty from
            
        Returns:
            Medical specialty if found, None otherwise
        """
        logger.debug(f"Extracting specialty from text ({len(text)} chars)")
        
        specialties = {
            "Cardiology": ["cardiology", "cardiologist", "heart", "cardiac"],
            "Neurology": ["neurology", "neurologist", "brain", "nerve"],
            "Gastroenterology": ["gastroenterology", "gastroenterologist", "digestive", "stomach", "gi"],
            "Pulmonology": ["pulmonology", "pulmonologist", "lung", "respiratory"],
            "Endocrinology": ["endocrinology", "endocrinologist", "hormone", "thyroid", "diabetes"],
            "Rheumatology": ["rheumatology", "rheumatologist", "arthritis", "joint", "autoimmune"],
            "Dermatology": ["dermatology", "dermatologist", "skin"],
            "Orthopedics": ["orthopedics", "orthopedist", "bone", "joint", "sports medicine"],
            "Gynecology": ["gynecology", "gynecologist", "obgyn", "women's health"],
            "Urology": ["urology", "urologist", "bladder", "kidney"],
            "Ophthalmology": ["ophthalmology", "ophthalmologist", "eye", "vision"],
            "ENT": ["ent", "ear nose and throat", "otolaryngology", "otolaryngologist", "ear", "nose", "throat"],
            "Psychiatry": ["psychiatry", "psychiatrist", "mental health"],
            "Nephrology": ["nephrology", "nephrologist", "kidney", "renal"],
            "Hematology": ["hematology", "hematologist", "blood"],
            "Oncology": ["oncology", "oncologist", "cancer"],
            "Primary Care": ["primary care", "family medicine", "general practice", "family doctor", "internist"]
        }
        
        text_lower = text.lower()
        
        # Look for direct mentions of specialties
        matches = {}
        for specialty, keywords in specialties.items():
            count = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    count += 1
            if count > 0:
                matches[specialty] = count
        
        if matches:
            # Return the specialty with the most matches
            return max(matches.items(), key=lambda x: x[1])[0]
        
        return None
    
    def extract_appointment_details(self, text: str) -> Dict[str, Any]:
        """Extract appointment details from text.
        
        Args:
            text: Medical text to extract appointment details from
            
        Returns:
            Dictionary containing appointment details
        """
        details = {
            "specialty": self.extract_specialty(text),
            "provider": self._extract_provider(text),
            "location": self._extract_location(text),
            "date": self._extract_date(text),
            "time": self._extract_time(text),
            "reason": self._extract_reason(text)
        }
        
        return details
    
    def _extract_conditions(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical conditions from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted condition entities
        """
        extracted = []
        text_lower = text.lower()
        
        # Check for each condition
        for condition_name, keywords in self.conditions.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Find the actual position of the keyword in text
                    matches = list(re.finditer(r'\b' + re.escape(keyword) + r'\b', text_lower))
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        
                        # Check for negation (simple rule-based approach)
                        context_start = max(0, start - 50)
                        context = text_lower[context_start:start]
                        negated = any(neg in context for neg in ["no ", "not ", "denies ", "negative for ", "absence of "])
                        
                        extracted.append({
                            "name": condition_name,
                            "text": text[start:end],
                            "start": start,
                            "end": end,
                            "negated": negated
                        })
                    break  # Found a match for this condition, move to next
        
        return extracted
    
    def _extract_medications(self, text: str) -> List[Dict[str, Any]]:
        """Extract medications from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted medication entities
        """
        extracted = []
        text_lower = text.lower()
        
        # First check for each medication in our dictionary
        for category, medications in self.medications.items():
            for medication in medications:
                if medication.lower() in text_lower:
                    # Find the actual positions of the medication in text
                    matches = list(re.finditer(r'\b' + re.escape(medication) + r'\b', text_lower))
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        
                        # Try to extract dosage (if any)
                        dosage = None
                        dosage_match = re.search(r'\b' + re.escape(medication) + r'\b\s+(\d+(?:\.\d+)?)\s?(mg|g|mcg|ml)', text_lower[end:end+20])
                        if dosage_match:
                            dosage = dosage_match.group(0)
                        
                        extracted.append({
                            "name": medication,
                            "category": category,
                            "text": text[start:end],
                            "dosage": dosage,
                            "start": start,
                            "end": end
                        })
                    
        # Also look for generic medication patterns
        med_patterns = [
            r'\b([A-Z][a-z]+(?:in|ol|ide|ine|one|ate|ium|en)\b)\s+(\d+(?:\.\d+)?)\s?(mg|g|mcg|ml)',  # Medication with dosage
            r'\b([A-Z][a-z]+(?:in|ol|ide|ine|one|ate|ium|en)\b)'  # Just medication name
        ]
        
        for pattern in med_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                medication_text = match.group(0)
                
                # Avoid duplicates with medications we've already found
                duplicate = False
                for existing in extracted:
                    if abs(match.start() - existing["start"]) < 10:  # Close match position
                        duplicate = True
                        break
                
                if not duplicate:
                    extracted.append({
                        "name": match.group(1) if pattern.endswith('\b') else medication_text,
                        "category": "Unknown",
                        "text": medication_text,
                        "dosage": medication_text if "mg" in medication_text or "g " in medication_text or "mcg" in medication_text else None,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return extracted
    
    def _extract_procedures(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical procedures from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted procedure entities
        """
        extracted = []
        
        # Define procedure types and regular expressions
        procedures = {
            "Imaging": [
                r'\b(?:MRI|Magnetic Resonance Imaging)\b(?:\s+of\s+(?:the\s+)?(\w+))?',
                r'\b(?:CT|CAT|Computed Tomography)\s+(?:scan|Scan)(?:\s+of\s+(?:the\s+)?(\w+))?',
                r'\b(?:X-ray|Xray|Radiograph)(?:\s+of\s+(?:the\s+)?(\w+))?',
                r'\b(?:Ultrasound|Sonogram|Ultrasonography)(?:\s+of\s+(?:the\s+)?(\w+))?',
                r'\b(?:PET|Positron Emission Tomography)\s+(?:scan|Scan)',
                r'\b(?:Mammogram|Mammography)\b'
            ],
            "Cardiology": [
                r'\b(?:ECG|EKG|Electrocardiogram)\b',
                r'\b(?:Echo|Echocardiogram|Cardiac Echo)\b',
                r'\b(?:Stress Test|Exercise Stress Test|Cardiac Stress Test)\b',
                r'\b(?:Cardiac Catheterization|Heart Cath)\b',
                r'\b(?:Holter Monitor)\b'
            ],
            "Gastroenterology": [
                r'\b(?:Colonoscopy)\b',
                r'\b(?:Endoscopy|Upper Endoscopy|EGD)\b',
                r'\b(?:Sigmoidoscopy)\b'
            ],
            "Neurology": [
                r'\b(?:EEG|Electroencephalogram)\b',
                r'\b(?:EMG|Electromyography)\b',
                r'\b(?:Nerve Conduction Study|NCS)\b'
            ],
            "Lab Tests": [
                r'\b(?:Blood Test|Blood Draw|Venipuncture|Phlebotomy)\b',
                r'\b(?:Urinalysis|Urine Test|Urine Sample)\b'
            ],
            "Surgical": [
                r'\b(?:Surgery|Surgical Procedure|Operation)\b(?:\s+(?:of|on|to)\s+(?:the\s+)?(\w+))?',
                r'\b(?:Biopsy)\b(?:\s+(?:of|on)\s+(?:the\s+)?(\w+))?',
                r'\b(?:Laparoscopy|Laparoscopic)\b'
            ]
        }
        
        # Check for each procedure group and pattern
        for category, patterns in procedures.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    procedure_text = match.group(0)
                    body_part = match.group(1) if match.lastindex else None
                    
                    extracted.append({
                        "category": category,
                        "text": procedure_text,
                        "body_part": body_part,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return extracted
    
    def _extract_lab_results(self, text: str) -> List[Dict[str, Any]]:
        """Extract lab results from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted lab result entities
        """
        extracted = []
        
        # Pattern for lab results with values
        lab_patterns = [
            r'\b(Hemoglobin|Hgb|Hb)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(g/dL|g/L)?',
            r'\b(White Blood (?:Cell|Count)|WBC)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(K/uL|x10\^9/L)?',
            r'\b(Platelet|PLT)(?:\s+(?:Count))?\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(K/uL|x10\^9/L)?',
            r'\b(Glucose|Blood Glucose|Blood Sugar)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(mg/dL|mmol/L)?',
            r'\b(A1C|HbA1C|Hemoglobin A1C)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(%)?',
            r'\b(Cholesterol|Total Cholesterol)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(mg/dL|mmol/L)?',
            r'\b(LDL|LDL-C|LDL Cholesterol)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(mg/dL|mmol/L)?',
            r'\b(HDL|HDL-C|HDL Cholesterol)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(mg/dL|mmol/L)?',
            r'\b(Triglycerides|TG)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(mg/dL|mmol/L)?',
            r'\b(TSH|Thyroid Stimulating Hormone)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(mIU/L|uIU/mL)?',
            r'\b(T4|Free T4|Thyroxine)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(ng/dL|pmol/L)?',
            r'\b(T3|Free T3|Triiodothyronine)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(pg/mL|pmol/L)?',
            r'\b(Vitamin D|25-OH Vitamin D|25-Hydroxyvitamin D)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(ng/mL|nmol/L)?',
            r'\b(Creatinine)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)\s*(mg/dL|umol/L)?',
            r'\b(BUN|Blood Urea Nitrogen)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(mg/dL|mmol/L)?',
            r'\b(eGFR|Estimated GFR|Glomerular Filtration Rate)\s+(?:is|was|of)?\s*:?\s*(\d+\.?\d*)',
            r'\b(ALT|SGPT|Alanine Transaminase)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(U/L|IU/L)?',
            r'\b(AST|SGOT|Aspartate Transaminase)\s+(?:is|was|of)?\s*:?\s*(\d+)\s*(U/L|IU/L)?'
        ]
        
        for pattern in lab_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                test_name = match.group(1)
                value = match.group(2)
                unit = match.group(3) if match.lastindex is not None and match.lastindex >= 3 else None
                
                extracted.append({
                    "name": test_name,
                    "value": value,
                    "unit": unit,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return extracted
    
    def _extract_vital_signs(self, text: str) -> List[Dict[str, Any]]:
        """Extract vital signs from text.
        
        Args:
            text: Medical text
            
        Returns:
            List of extracted vital sign entities
        """
        extracted = []
        
        # Patterns for vital signs
        vital_patterns = [
            r'\b(?:Blood Pressure|BP)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{2,3})/(\d{2,3})\s*(mmHg)?',
            r'\b(?:Heart Rate|HR|Pulse)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{2,3})\s*(bpm|BPM)?',
            r'\b(?:Temperature|Temp)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{2,3}\.?\d*)\s*(°F|F|°C|C)?',
            r'\b(?:Respiratory Rate|RR|Respiration)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{1,2})\s*(breaths/min)?',
            r'\b(?:Oxygen Saturation|O2 Sat|SpO2|Pulse Ox)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{1,3})(?:\s*|\s*%)',
            r'\b(?:Weight)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{2,3}\.?\d*)\s*(kg|lbs|pounds)?',
            r'\b(?:Height)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{1,3}\'(?:\d{1,2}\")?|\d{2,3}(?:\.\d+)?)\s*(cm|in|inches)?',
            r'\b(?:BMI|Body Mass Index)(?:\s+(?:is|was|of))?(?:\s+|:)\s*(\d{1,3}(?:\.\d+)?)'
        ]
        
        for pattern in vital_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                match_text = match.group(0)
                if match_text:
                    name = re.search(r'^[^(]*', match_text)
                    if name:
                        name = name.group(0).strip()
                    else:
                        continue  # Skip if we can't extract the name
                        
                    value = match.group(1)
                    
                    # Special case for BP which has systolic/diastolic
                    if "Blood Pressure" in name or "BP" in name:
                        value = f"{match.group(1)}/{match.group(2)}"
                        unit = match.group(3) if match.lastindex is not None and match.lastindex >= 3 else "mmHg"
                    else:
                        unit = match.group(2) if match.lastindex is not None and match.lastindex >= 2 else None
                    
                    extracted.append({
                        "name": name,
                        "value": value,
                        "unit": unit,
                        "text": match_text,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        return extracted
    
    def _extract_provider(self, text: str) -> Optional[str]:
        """Extract healthcare provider name from text."""
        # Look for common patterns indicating provider names
        patterns = [
            r'(?:Dr\.|Doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:Provider|Physician|Clinician):\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:seen by|evaluated by|consulted with)\s+(?:Dr\.|Doctor)?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract healthcare location from text."""
        # Look for common patterns indicating healthcare locations
        patterns = [
            r'(?:at|in)\s+(?:the\s+)?([A-Z][a-zA-Z\s]+(?:Hospital|Clinic|Medical Center|Center|Practice|Office))',
            r'(?:Location|Facility|Site):\s+([A-Z][a-zA-Z\s]+(?:Hospital|Clinic|Medical Center|Center|Practice|Office))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text."""
        # Common date patterns
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{1,2}-\d{1,2}-\d{2,4})',  # MM-DD-YYYY or DD-MM-YYYY
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})'  # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time from text."""
        # Common time patterns
        patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))',  # HH:MM am/pm
            r'(\d{1,2}\s*(?:am|pm|AM|PM))'  # HH am/pm
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_reason(self, text: str) -> Optional[str]:
        """Extract reason for appointment from text."""
        # Common patterns for appointment reasons
        patterns = [
            r'(?:Reason for visit|Chief complaint|Appointment reason):\s*(.+?)(?:\.|$)',
            r'(?:Presenting with|Presents with|Here for):\s*(.+?)(?:\.|$)',
            r'(?:Visit for|Appointment for):\s*(.+?)(?:\.|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None 