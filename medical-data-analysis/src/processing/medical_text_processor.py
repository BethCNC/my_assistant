import re
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from datetime import datetime

from src.processing.base import BaseProcessor

class MedicalTextProcessor(BaseProcessor):
    """Processor for medical text data with specialized medical entity extraction."""
    
    def __init__(self):
        super().__init__()
        
        # Medical entity patterns
        self.medication_pattern = re.compile(
            r'\b(([A-Z][a-z]+\s?)+)\s+(\d+\.?\d*)\s*(mg|mcg|g|ml|%|mg/ml|mcg/ml)\b',
            re.IGNORECASE
        )
        
        self.vital_signs_pattern = re.compile(
            r'\b(BP|Blood Pressure|HR|Heart Rate|RR|Respiratory Rate|O2|Oxygen|Temp|Temperature)[\s:]+([\\d\\.]+(?:[\\s/]\\d+)?)',
            re.IGNORECASE
        )
        
        self.observation_pattern = re.compile(
            r'\b(note|notes|observed|observes|shows|demonstrates|exhibits|presents with|displays|manifests)\b',
            re.IGNORECASE
        )
        
        self.provider_pattern = re.compile(
            r'(?:Provider|Physician|Doctor|Attending|Consultant):\s*(?:Dr\.\s*)?([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s*,\s*([^,\n]+))?',
            re.IGNORECASE
        )
        
        # Common specialties and their related terms
        self.specialties = {
            "rheumatology": [
                "rheumatologist", "rheumatology", "arthritis", "autoimmune", "joint", 
                "inflammation", "lupus", "EDS", "hypermobility", "Ehlers-Danlos"
            ],
            "neurology": [
                "neurologist", "neurology", "brain", "nerve", "migraine", "seizure",
                "headache", "MS", "multiple sclerosis", "dysautonomia", "POTS"
            ],
            "cardiology": [
                "cardiologist", "cardiology", "heart", "cardiac", "palpitations", 
                "arrhythmia", "hypertension", "ECG", "EKG"
            ],
            "gastroenterology": [
                "gastroenterologist", "gastroenterology", "GI", "digestive", "stomach",
                "intestinal", "bowel", "GERD", "IBS", "Crohn", "colitis"
            ],
            "psychiatry": [
                "psychiatrist", "psychiatry", "mental health", "depression", "anxiety",
                "ADHD", "autism", "ASD", "bipolar", "psychiatric"
            ]
        }
        
        # Common sections in clinical notes
        self.clinical_sections = [
            "chief complaint", "history of present illness", "past medical history",
            "medications", "allergies", "family history", "social history", 
            "review of systems", "physical examination", "assessment", "plan",
            "impression", "diagnosis", "follow-up"
        ]
        
    def process(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process extracted medical text data to organize and structure the information.
        
        Args:
            extraction_data: Data from an extractor
            
        Returns:
            Processed and structured medical data
        """
        processed_data = {}
        
        # Preserve original metadata
        if "metadata" in extraction_data:
            processed_data["metadata"] = extraction_data["metadata"]
        
        # Get content
        content = extraction_data.get("content", "")
        if not content:
            return {"error": "No content to process"}
        
        # Process providers
        if "providers" in extraction_data:
            processed_data["providers"] = self._process_providers(extraction_data["providers"])
        else:
            # Try to extract providers if not provided
            processed_data["providers"] = []
        
        # Process appointment dates
        if "appointment_dates" in extraction_data:
            processed_data["appointment_dates"] = self._process_appointment_dates(extraction_data["appointment_dates"])
        else:
            processed_data["appointment_dates"] = []
        
        # Process doctor notes
        if "doctor_notes" in extraction_data:
            processed_data["doctor_notes"] = self._process_doctor_notes(extraction_data["doctor_notes"])
        else:
            processed_data["doctor_notes"] = []
        
        # Process clinical sections
        clinical_sections = {}
        if "clinical_sections" in extraction_data:
            clinical_sections = extraction_data["clinical_sections"]
            processed_data["clinical_sections"] = clinical_sections
        
        # Extract clinical observations
        processed_data["clinical_observations"] = self._extract_clinical_observations(content, clinical_sections)
        
        # Extract diagnoses and conditions
        processed_data["diagnoses"] = self._extract_diagnoses(content, clinical_sections)
        
        # Extract treatment plan
        processed_data["treatment_plan"] = self._extract_treatment_plan(content, clinical_sections)
        
        # Extract medications
        processed_data["medications"] = self._extract_medications(content, clinical_sections)
        
        # Create a clinical summary
        processed_data["clinical_summary"] = self._create_clinical_summary(processed_data)
        
        return processed_data
    
    def _process_providers(self, providers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and deduplicate provider information."""
        if not providers:
            return []
        
        # Use a set to track processed provider names
        processed_names = set()
        processed_providers = []
        
        for provider in providers:
            name = provider.get("name", "").strip()
            if not name or name in processed_names:
                continue
                
            processed_names.add(name)
            
            # Clean and standardize provider data
            processed_provider = {
                "name": name,
                "specialty": provider.get("specialty"),
                "confidence": provider.get("confidence", 0.5)
            }
            
            # Try to infer specialty if not provided
            if not processed_provider["specialty"] and "context" in provider:
                context = provider["context"].lower()
                for specialty, keywords in self.specialties.items():
                    if any(keyword.lower() in context for keyword in keywords):
                        processed_provider["specialty"] = specialty
                        break
            
            processed_providers.append(processed_provider)
        
        return processed_providers
    
    def _process_appointment_dates(self, appointment_dates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and normalize appointment dates."""
        if not appointment_dates:
            return []
        
        processed_dates = []
        
        for appt in appointment_dates:
            date = appt.get("date", "")
            if not date:
                continue
                
            processed_appt = {
                "date": date,
                "type": appt.get("type", "appointment")
            }
            
            # Extract provider information if available in context
            if "context" in appt:
                context = appt["context"]
                
                # Look for provider names in context
                provider_match = self.provider_pattern.search(context)
                if provider_match:
                    processed_appt["provider"] = provider_match.group(1)
                    if provider_match.group(2):
                        processed_appt["specialty"] = provider_match.group(2)
            
            processed_dates.append(processed_appt)
        
        return processed_dates
    
    def _process_doctor_notes(self, doctor_notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and categorize doctor's notes."""
        if not doctor_notes:
            return []
        
        processed_notes = []
        
        for note in doctor_notes:
            note_text = note.get("note", "")
            if not note_text:
                continue
                
            processed_note = {
                "note": note_text,
                "type": note.get("type", "general"),
                "doctor": note.get("doctor")
            }
            
            # Add section information if available
            if "section" in note:
                processed_note["section"] = note["section"]
            
            # Try to categorize the note
            if "ASSESSMENT" in note.get("section", ""):
                processed_note["category"] = "assessment"
            elif "PLAN" in note.get("section", ""):
                processed_note["category"] = "plan"
            elif "IMPRESSION" in note.get("section", ""):
                processed_note["category"] = "impression"
            elif note.get("type") == "quote":
                processed_note["category"] = "quote"
            else:
                processed_note["category"] = "other"
            
            processed_notes.append(processed_note)
        
        return processed_notes
    
    def _extract_clinical_observations(self, content: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract clinical observations from the text."""
        observations = []
        
        # Look for observations in physical examination and other relevant sections
        relevant_sections = ["PHYSICAL EXAMINATION", "PHYSICAL EXAM", "EXAM", "FINDINGS", "OBSERVATIONS"]
        
        for section_name, section_content in sections.items():
            if any(rel.upper() in section_name.upper() for rel in relevant_sections):
                # Split section into lines/sentences
                lines = re.split(r'[.\n]', section_content)
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Look for observational language
                    if self.observation_pattern.search(line) or ":" in line:
                        observations.append({
                            "observation": line,
                            "source": section_name,
                            "category": self._categorize_observation(line)
                        })
        
        # Check for vitals
        vitals_sections = ["VITAL SIGNS", "VITALS"]
        vitals_pattern = re.compile(r'(BP|HR|RR|Temp|O2)[:\s]+(\d+(?:[/\.]\d+)?)', re.IGNORECASE)
        
        for section_name, section_content in sections.items():
            if any(vital.upper() in section_name.upper() for vital in vitals_sections):
                for match in vitals_pattern.finditer(section_content):
                    vital_type = match.group(1).upper()
                    value = match.group(2)
                    observations.append({
                        "observation": f"{vital_type}: {value}",
                        "source": section_name,
                        "category": "vitals",
                        "vital_type": vital_type,
                        "value": value
                    })
        
        return observations
    
    def _categorize_observation(self, observation: str) -> str:
        """Categorize clinical observations by body system or type."""
        observation_lower = observation.lower()
        
        # Categorize based on content
        if any(term in observation_lower for term in ["joint", "hypermobility", "beighton", "skin", "scar", "bruise"]):
            return "connective_tissue"
        elif any(term in observation_lower for term in ["heart", "pulse", "cardiac", "bp", "blood pressure"]):
            return "cardiovascular"
        elif any(term in observation_lower for term in ["lung", "breath", "respiratory", "breathing"]):
            return "respiratory"
        elif any(term in observation_lower for term in ["abdomen", "bowel", "intestinal", "gi"]):
            return "gastrointestinal"
        elif any(term in observation_lower for term in ["neuro", "reflex", "coordination", "balance", "sensation"]):
            return "neurological"
        elif any(term in observation_lower for term in ["mental", "mood", "affect", "cognition", "attention"]):
            return "psychiatric"
        else:
            return "general"
    
    def _extract_diagnoses(self, content: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract diagnoses and conditions from the text."""
        diagnoses = []
        
        # Look for diagnoses in assessment and impression sections
        relevant_sections = ["ASSESSMENT", "IMPRESSION", "DIAGNOSIS", "DIAGNOSES"]
        
        for section_name, section_content in sections.items():
            if any(rel.upper() in section_name.upper() for rel in relevant_sections):
                # Look for numbered lists which often indicate diagnoses
                numbered_items = re.findall(r'(?m)^\s*(\d+\.|\d+\)|\d+:)\s*(.+)$', section_content)
                
                if numbered_items:
                    for _, item in numbered_items:
                        diagnoses.append({
                            "condition": item.strip(),
                            "source": section_name,
                            "confidence": 0.9
                        })
                else:
                    # Split by lines/sentences
                    lines = re.split(r'[.\n]', section_content)
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 5:  # Arbitrary minimum to avoid fragments
                            diagnoses.append({
                                "condition": line,
                                "source": section_name,
                                "confidence": 0.7
                            })
        
        return diagnoses
    
    def _extract_treatment_plan(self, content: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract treatment plan items from the text."""
        plan_items = []
        
        # Look for plan items in plan section
        relevant_sections = ["PLAN", "TREATMENT PLAN", "RECOMMENDATIONS", "FOLLOW-UP"]
        
        for section_name, section_content in sections.items():
            if any(rel.upper() in section_name.upper() for rel in relevant_sections):
                # Look for numbered or bulleted lists
                list_items = re.findall(r'(?m)^\s*(?:\d+\.|\d+\)|\d+:|\*|\-)\s*(.+)$', section_content)
                
                if list_items:
                    for item in list_items:
                        item_text = item.strip()
                        plan_items.append({
                            "item": item_text,
                            "source": section_name,
                            "type": self._categorize_plan_item(item_text)
                        })
                else:
                    # Split by lines/sentences
                    lines = re.split(r'[.\n]', section_content)
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 5:  # Arbitrary minimum to avoid fragments
                            plan_items.append({
                                "item": line,
                                "source": section_name,
                                "type": self._categorize_plan_item(line)
                            })
        
        return plan_items
    
    def _categorize_plan_item(self, plan_item: str) -> str:
        """Categorize treatment plan items by type."""
        plan_lower = plan_item.lower()
        
        # Categorize based on content
        if any(term in plan_lower for term in ["lab", "test", "mri", "ct", "scan", "blood", "panel", "x-ray"]):
            return "testing"
        elif any(term in plan_lower for term in ["refer", "referral", "specialist", "consult", "consultation"]):
            return "referral"
        elif any(term in plan_lower for term in ["follow", "return", "schedule", "appointment", "weeks", "months"]):
            return "follow_up"
        elif any(term in plan_lower for term in ["medic", "prescription", "dose", "mg", "treatment"]):
            return "medication"
        elif any(term in plan_lower for term in ["therapy", "pt", "ot", "physical therapy", "occupational therapy"]):
            return "therapy"
        elif any(term in plan_lower for term in ["diet", "exercise", "activity", "lifestyle"]):
            return "lifestyle"
        else:
            return "other"
    
    def _extract_medications(self, content: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract medications from the text."""
        medications = []
        
        # Look for medications in medication section and other sections
        relevant_sections = ["MEDICATIONS", "CURRENT MEDICATIONS", "PRESCRIPTIONS"]
        
        for section_name, section_content in sections.items():
            if any(rel.upper() in section_name.upper() for rel in relevant_sections):
                # Look for medication patterns
                for match in self.medication_pattern.finditer(section_content):
                    medications.append({
                        "medication": match.group(1).strip(),
                        "dosage": match.group(3),
                        "unit": match.group(4),
                        "source": section_name
                    })
                
                # Also look for list items which might be medications
                list_items = re.findall(r'(?m)^\s*(?:\d+\.|\d+\)|\d+:|\*|\-)\s*(.+)$', section_content)
                
                for item in list_items:
                    # Check if this item wasn't already matched by the medication pattern
                    if not any(med["medication"].lower() in item.lower() for med in medications):
                        # Check for common medication words/patterns
                        med_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(\d+\.?\d*)\s*(mg|mcg|g|ml|%)', item, re.IGNORECASE)
                        if med_match:
                            medications.append({
                                "medication": med_match.group(1).strip(),
                                "dosage": med_match.group(2),
                                "unit": med_match.group(3),
                                "source": section_name
                            })
        
        return medications
    
    def _create_clinical_summary(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the clinical data."""
        summary = {
            "appointment_info": None,
            "providers": [],
            "diagnoses": [],
            "treatment_plan": [],
            "medications": [],
            "key_observations": []
        }
        
        # Add appointment information
        if processed_data.get("appointment_dates"):
            summary["appointment_info"] = {
                "date": processed_data["appointment_dates"][0].get("date"),
                "type": processed_data["appointment_dates"][0].get("type")
            }
        
        # Add providers
        if processed_data.get("providers"):
            # Sort by confidence score if available
            providers = sorted(
                processed_data["providers"], 
                key=lambda p: p.get("confidence", 0), 
                reverse=True
            )
            summary["providers"] = providers[:3]  # Limit to top 3
        
        # Add diagnoses
        if processed_data.get("diagnoses"):
            # Sort by confidence score if available
            diagnoses = sorted(
                processed_data["diagnoses"], 
                key=lambda d: d.get("confidence", 0), 
                reverse=True
            )
            summary["diagnoses"] = diagnoses[:5]  # Limit to top 5
        
        # Add treatment plan
        if processed_data.get("treatment_plan"):
            summary["treatment_plan"] = processed_data["treatment_plan"]
        
        # Add medications
        if processed_data.get("medications"):
            summary["medications"] = processed_data["medications"]
        
        # Add key observations
        if processed_data.get("clinical_observations"):
            # Group observations by category
            observations_by_category = {}
            for obs in processed_data["clinical_observations"]:
                category = obs.get("category", "general")
                if category not in observations_by_category:
                    observations_by_category[category] = []
                observations_by_category[category].append(obs)
            
            # Add a representative observation from each category
            for category, observations in observations_by_category.items():
                if observations:
                    summary["key_observations"].append(observations[0])
        
        return summary
    
    def specialized_processing(self) -> None:
        """
        Implement specialized processing for medical text as required by BaseProcessor.
        This enhances self.data with additional processed medical information.
        """
        if not self.data.get("content"):
            return
        
        content = self.data.get("content", "")
        
        # Extract clinical sections if not already present
        if "clinical_sections" not in self.data:
            self.data["clinical_sections"] = self.extract_sections(content)
        
        # Extract clinical observations
        self.data["clinical_observations"] = self._extract_clinical_observations(
            content, self.data.get("clinical_sections", {})
        )
        
        # Extract diagnoses and conditions
        self.data["diagnoses"] = self._extract_diagnoses(
            content, self.data.get("clinical_sections", {})
        )
        
        # Extract treatment plan
        self.data["treatment_plan"] = self._extract_treatment_plan(
            content, self.data.get("clinical_sections", {})
        )
        
        # Extract medications
        self.data["medications"] = self._extract_medications(
            content, self.data.get("clinical_sections", {})
        )
        
        # Create a clinical summary
        self.data["clinical_summary"] = self._create_clinical_summary(self.data)
    
    def extract_providers(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract healthcare providers mentioned in the text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of dictionaries with provider information
        """
        providers = []
        
        # Standard provider extraction
        for match in self.provider_pattern.finditer(text):
            provider_name = match.group(1).strip()
            specialty = match.group(2).strip() if match.group(2) else None
            
            # Try to identify specialty from surrounding context
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end].lower()
            
            if not specialty:
                for spec, keywords in self.specialties.items():
                    for keyword in keywords:
                        if keyword in context:
                            specialty = spec
                            break
                    if specialty:
                        break
            
            providers.append({
                "name": provider_name,
                "specialty": specialty,
                "context": context
            })
        
        return providers
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections from clinical notes based on common headers.
        
        Args:
            text: Clinical note text
            
        Returns:
            Dictionary of section names and their contents
        """
        sections = {}
        
        # Look for common section headers in all caps followed by colon
        section_pattern = re.compile(r'^([A-Z][A-Z\s]+):\s*$|^([A-Z][A-Z\s]+):\s*(.+)$', re.MULTILINE)
        matches = list(section_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            # Get section name
            section_name = (match.group(1) or match.group(2)).strip()
            
            # Get section content from this section to the start of the next one (or end of text)
            section_start = match.end()
            section_end = matches[i+1].start() if i < len(matches) - 1 else len(text)
            
            # If the section header had content on the same line
            if match.group(3):
                section_content = match.group(3) + text[match.end():section_end].strip()
            else:
                section_content = text[section_start:section_end].strip()
                
            sections[section_name] = section_content
            
        return sections 