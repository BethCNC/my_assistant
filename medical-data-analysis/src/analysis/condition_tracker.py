"""
Condition Tracker Module

This module provides functionality to track and analyze medical conditions
across multiple documents, with special focus on EDS, POTS, MCAS, and ASD.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConditionTracker:
    """
    Tracks and analyzes medical conditions across documents,
    with special focus on complex conditions like EDS, POTS, MCAS, and ASD.
    """
    
    # Define condition keywords and synonyms
    CONDITION_KEYWORDS = {
        "eds": [
            "ehlers-danlos", "ehlers danlos", "hypermobility syndrome", 
            "joint hypermobility", "eds", "hypermobile", "heds", "ceds", "veds",
            "connective tissue disorder", "connective tissue disease"
        ],
        "pots": [
            "postural orthostatic tachycardia", "pots", "dysautonomia", 
            "orthostatic intolerance", "tachycardia syndrome", 
            "orthostatic tachycardia"
        ],
        "mcas": [
            "mast cell activation", "mcas", "mast cell disorder", 
            "mast cell disease", "mastocytosis", "histamine intolerance"
        ],
        "asd": [
            "autism spectrum", "asd", "asperger", "autistic", "autism", 
            "neurodevelopmental disorder", "neurodivergent"
        ],
        "adhd": [
            "attention deficit", "adhd", "add", "hyperactivity disorder",
            "executive dysfunction", "executive function disorder"
        ],
        "gastro": [
            "irritable bowel", "ibs", "gastroesophageal reflux", "gerd",
            "acid reflux", "crohn", "colitis", "celiac", "gastroparesis"
        ],
        "chronic_pain": [
            "chronic pain", "fibromyalgia", "myalgia", "arthralgia", 
            "neuropathy", "neuropathic pain", "persistent pain"
        ],
        "autoimmune": [
            "autoimmune", "rheumatoid arthritis", "lupus", "sjogren", 
            "hashimoto", "multiple sclerosis", "psoriasis", "vasculitis"
        ]
    }
    
    # EDS-specific criteria (based on 2017 diagnostic criteria)
    EDS_CRITERIA = {
        "hypermobility": [
            "beighton score", "hypermobile joints", "hyperextensible joints",
            "joint laxity", "joint hypermobility", "flexible joints", 
            "double jointed", "joint dislocation", "joint subluxation"
        ],
        "skin_issues": [
            "skin hyperextensibility", "stretchy skin", "elastic skin",
            "soft skin", "velvety skin", "thin skin", "translucent skin",
            "easy bruising", "bruises easily", "poor wound healing", 
            "atrophic scarring", "widened scars", "cigarette paper scars"
        ],
        "joint_problems": [
            "joint dislocation", "joint subluxation", "joint instability",
            "recurrent dislocations", "chronic joint pain", "early osteoarthritis"
        ],
        "systemic_manifestations": [
            "aortic root dilation", "mitral valve prolapse", "mvp",
            "arterial fragility", "arterial rupture", "tissue fragility",
            "pectus excavatum", "pectus carinatum", "scoliosis",
            "high palate", "dental crowding", "hernia", "herniation"
        ]
    }
    
    # POTS specific symptoms
    POTS_SYMPTOMS = [
        "lightheadedness", "dizziness", "fainting", "syncope", "presyncope",
        "heart palpitations", "rapid heartbeat", "tachycardia", 
        "heart rate increase", "exercise intolerance", "fatigue",
        "blood pooling", "acrocyanosis", "brain fog", "cognitive impairment",
        "headache", "nausea", "tremor", "poor concentration"
    ]
    
    # MCAS specific symptoms
    MCAS_SYMPTOMS = [
        "flushing", "hives", "urticaria", "itching", "pruritus", 
        "angioedema", "swelling", "dermatographism", "rash",
        "abdominal pain", "cramping", "diarrhea", "nausea", "heartburn",
        "wheezing", "shortness of breath", "throat tightness", 
        "nasal congestion", "anaphylaxis", "anaphylactoid",
        "food intolerance", "drug sensitivity", "chemical sensitivity"
    ]
    
    # ASD specific traits
    ASD_TRAITS = [
        "social communication difficulty", "social interaction difficulty",
        "repetitive behavior", "restricted interests", "intense interests",
        "sensory sensitivity", "sensory issues", "sensory processing",
        "stimming", "self-stimulatory behavior", "echolalia",
        "literal interpretation", "difficulty with figurative language",
        "difficulty reading social cues", "eye contact difficulty",
        "need for routine", "resistance to change", "meltdown", "shutdown"
    ]
    
    def __init__(self):
        """Initialize the condition tracker."""
        # Store condition mentions with document references
        self.condition_mentions = defaultdict(list)
        
        # Store evidence for specific conditions
        self.condition_evidence = defaultdict(lambda: defaultdict(list))
        
        # Store chronological history of condition mentions
        self.condition_timeline = []
    
    def analyze_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a document for condition mentions and evidence.
        
        Args:
            document_data: Document data dictionary
            
        Returns:
            Updated document data with condition analysis
        """
        try:
            # Extract basic document info
            doc_id = document_data.get("id", "unknown")
            content = document_data.get("content", "").lower()
            date_str = document_data.get("metadata", {}).get("date")
            
            # Parse document date
            doc_date = None
            if date_str:
                try:
                    doc_date = datetime.fromisoformat(date_str)
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse document date: {date_str}")
            
            # Find condition mentions
            found_conditions = self._find_condition_mentions(content)
            
            # If conditions were found, record them
            if found_conditions:
                # Add to document data
                if "processed_data" not in document_data:
                    document_data["processed_data"] = {}
                
                document_data["processed_data"]["conditions"] = {
                    condition: {
                        "mentioned": True,
                        "evidence": evidence
                    } for condition, evidence in found_conditions.items()
                }
                
                # Update metadata
                document_data["metadata"] = document_data.get("metadata", {})
                document_data["metadata"]["conditions"] = list(found_conditions.keys())
                
                # Record in condition tracker
                self._record_condition_mentions(doc_id, doc_date, found_conditions, document_data)
            
            return document_data
        except Exception as e:
            logger.error(f"Error analyzing document for conditions: {e}")
            return document_data
    
    def _find_condition_mentions(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find mentions of tracked conditions in document content.
        
        Args:
            content: Document content
            
        Returns:
            Dictionary mapping conditions to evidence
        """
        found_conditions = {}
        
        # Search for main condition keywords
        for condition, keywords in self.CONDITION_KEYWORDS.items():
            evidence = []
            
            for keyword in keywords:
                # Find all instances of the keyword
                start_idx = 0
                while True:
                    pos = content.find(keyword, start_idx)
                    if pos == -1:
                        break
                    
                    # Extract context (100 chars before and after)
                    context_start = max(0, pos - 100)
                    context_end = min(len(content), pos + len(keyword) + 100)
                    context = content[context_start:context_end]
                    
                    evidence.append({
                        "keyword": keyword,
                        "context": context,
                        "position": pos
                    })
                    
                    # Move start index to avoid finding the same instance again
                    start_idx = pos + len(keyword)
            
            if evidence:
                found_conditions[condition] = evidence
        
        # Add specific criteria for main conditions
        self._add_eds_criteria(content, found_conditions)
        self._add_pots_symptoms(content, found_conditions)
        self._add_mcas_symptoms(content, found_conditions)
        self._add_asd_traits(content, found_conditions)
        
        return found_conditions
    
    def _add_eds_criteria(self, content: str, found_conditions: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Add specific EDS criteria evidence.
        
        Args:
            content: Document content
            found_conditions: Dictionary of found conditions to update
        """
        eds_evidence = []
        
        for category, criteria in self.EDS_CRITERIA.items():
            for criterion in criteria:
                # Find all instances of the criterion
                start_idx = 0
                while True:
                    pos = content.find(criterion, start_idx)
                    if pos == -1:
                        break
                    
                    # Extract context
                    context_start = max(0, pos - 100)
                    context_end = min(len(content), pos + len(criterion) + 100)
                    context = content[context_start:context_end]
                    
                    eds_evidence.append({
                        "keyword": criterion,
                        "category": category,
                        "context": context,
                        "position": pos
                    })
                    
                    # Move start index
                    start_idx = pos + len(criterion)
        
        if eds_evidence:
            if "eds" in found_conditions:
                found_conditions["eds"].extend(eds_evidence)
            else:
                found_conditions["eds"] = eds_evidence
    
    def _add_pots_symptoms(self, content: str, found_conditions: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Add specific POTS symptom evidence.
        
        Args:
            content: Document content
            found_conditions: Dictionary of found conditions to update
        """
        pots_evidence = []
        
        for symptom in self.POTS_SYMPTOMS:
            # Find all instances of the symptom
            start_idx = 0
            while True:
                pos = content.find(symptom, start_idx)
                if pos == -1:
                    break
                
                # Extract context
                context_start = max(0, pos - 100)
                context_end = min(len(content), pos + len(symptom) + 100)
                context = content[context_start:context_end]
                
                pots_evidence.append({
                    "keyword": symptom,
                    "category": "symptom",
                    "context": context,
                    "position": pos
                })
                
                # Move start index
                start_idx = pos + len(symptom)
        
        if pots_evidence:
            if "pots" in found_conditions:
                found_conditions["pots"].extend(pots_evidence)
            else:
                found_conditions["pots"] = pots_evidence
    
    def _add_mcas_symptoms(self, content: str, found_conditions: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Add specific MCAS symptom evidence.
        
        Args:
            content: Document content
            found_conditions: Dictionary of found conditions to update
        """
        mcas_evidence = []
        
        for symptom in self.MCAS_SYMPTOMS:
            # Find all instances of the symptom
            start_idx = 0
            while True:
                pos = content.find(symptom, start_idx)
                if pos == -1:
                    break
                
                # Extract context
                context_start = max(0, pos - 100)
                context_end = min(len(content), pos + len(symptom) + 100)
                context = content[context_start:context_end]
                
                mcas_evidence.append({
                    "keyword": symptom,
                    "category": "symptom",
                    "context": context,
                    "position": pos
                })
                
                # Move start index
                start_idx = pos + len(symptom)
        
        if mcas_evidence:
            if "mcas" in found_conditions:
                found_conditions["mcas"].extend(mcas_evidence)
            else:
                found_conditions["mcas"] = mcas_evidence
    
    def _add_asd_traits(self, content: str, found_conditions: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Add specific ASD trait evidence.
        
        Args:
            content: Document content
            found_conditions: Dictionary of found conditions to update
        """
        asd_evidence = []
        
        for trait in self.ASD_TRAITS:
            # Find all instances of the trait
            start_idx = 0
            while True:
                pos = content.find(trait, start_idx)
                if pos == -1:
                    break
                
                # Extract context
                context_start = max(0, pos - 100)
                context_end = min(len(content), pos + len(trait) + 100)
                context = content[context_start:context_end]
                
                asd_evidence.append({
                    "keyword": trait,
                    "category": "trait",
                    "context": context,
                    "position": pos
                })
                
                # Move start index
                start_idx = pos + len(trait)
        
        if asd_evidence:
            if "asd" in found_conditions:
                found_conditions["asd"].extend(asd_evidence)
            else:
                found_conditions["asd"] = asd_evidence
    
    def _record_condition_mentions(
        self, 
        doc_id: str, 
        doc_date: Optional[datetime], 
        conditions: Dict[str, List[Dict[str, Any]]],
        document_data: Dict[str, Any]
    ) -> None:
        """
        Record condition mentions in the tracker.
        
        Args:
            doc_id: Document ID
            doc_date: Document date
            conditions: Dictionary of conditions and evidence
            document_data: Original document data
        """
        doc_info = {
            "id": doc_id,
            "date": doc_date,
            "title": document_data.get("metadata", {}).get("title", "Unknown"),
            "provider": document_data.get("metadata", {}).get("provider"),
            "specialty": document_data.get("metadata", {}).get("specialty")
        }
        
        # Record in condition mentions
        for condition, evidence in conditions.items():
            self.condition_mentions[condition].append({
                "document": doc_info,
                "evidence_count": len(evidence)
            })
            
            # Record specific evidence
            for item in evidence:
                self.condition_evidence[condition][item.get("category", "general")].append({
                    "document": doc_info,
                    "keyword": item.get("keyword"),
                    "context": item.get("context")
                })
        
        # Add to timeline
        timeline_entry = {
            "document": doc_info,
            "conditions": list(conditions.keys())
        }
        
        self.condition_timeline.append(timeline_entry)
        
        # Sort timeline by date
        self.condition_timeline.sort(
            key=lambda x: (
                x["document"]["date"] if x["document"]["date"] else datetime.max
            )
        )
    
    def get_condition_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all tracked conditions.
        
        Returns:
            Dictionary with condition summary information
        """
        summary = {}
        
        for condition, mentions in self.condition_mentions.items():
            # Count mentions
            mention_count = len(mentions)
            
            # Get earliest and latest mention dates
            dates = [
                mention["document"]["date"] 
                for mention in mentions 
                if mention["document"]["date"]
            ]
            
            first_mention = min(dates) if dates else None
            latest_mention = max(dates) if dates else None
            
            # Get providers who mentioned the condition
            providers = set(
                mention["document"]["provider"] 
                for mention in mentions 
                if mention["document"]["provider"]
            )
            
            # Get specialties who mentioned the condition
            specialties = set(
                mention["document"]["specialty"] 
                for mention in mentions 
                if mention["document"]["specialty"]
            )
            
            # Count evidence by category
            evidence_by_category = {}
            for category, items in self.condition_evidence[condition].items():
                evidence_by_category[category] = len(items)
            
            # Create summary for this condition
            summary[condition] = {
                "mention_count": mention_count,
                "first_mention": first_mention.isoformat() if first_mention else None,
                "latest_mention": latest_mention.isoformat() if latest_mention else None,
                "providers": list(providers),
                "specialties": list(specialties),
                "evidence_by_category": evidence_by_category
            }
            
            # Add condition-specific metrics
            self._add_condition_specific_metrics(condition, summary[condition])
        
        return summary
    
    def _add_condition_specific_metrics(self, condition: str, summary: Dict[str, Any]) -> None:
        """
        Add condition-specific metrics to the summary.
        
        Args:
            condition: Condition name
            summary: Summary dictionary to update
        """
        if condition == "eds":
            # Calculate EDS criteria coverage
            criteria_categories = set(self.condition_evidence[condition].keys())
            eds_criteria_categories = set(self.EDS_CRITERIA.keys())
            criteria_coverage = len(criteria_categories.intersection(eds_criteria_categories)) / len(eds_criteria_categories)
            
            summary["criteria_coverage"] = criteria_coverage
            summary["criteria_categories"] = list(criteria_categories.intersection(eds_criteria_categories))
        
        elif condition == "pots":
            # Calculate symptom coverage
            symptom_count = sum(
                1 for evidence in self.condition_evidence[condition].get("symptom", [])
                if evidence["keyword"] in self.POTS_SYMPTOMS
            )
            symptom_coverage = symptom_count / len(self.POTS_SYMPTOMS) if self.POTS_SYMPTOMS else 0
            
            summary["symptom_coverage"] = symptom_coverage
            summary["symptom_count"] = symptom_count
        
        elif condition == "mcas":
            # Calculate symptom coverage
            symptom_count = sum(
                1 for evidence in self.condition_evidence[condition].get("symptom", [])
                if evidence["keyword"] in self.MCAS_SYMPTOMS
            )
            symptom_coverage = symptom_count / len(self.MCAS_SYMPTOMS) if self.MCAS_SYMPTOMS else 0
            
            summary["symptom_coverage"] = symptom_coverage
            summary["symptom_count"] = symptom_count
        
        elif condition == "asd":
            # Calculate trait coverage
            trait_count = sum(
                1 for evidence in self.condition_evidence[condition].get("trait", [])
                if evidence["keyword"] in self.ASD_TRAITS
            )
            trait_coverage = trait_count / len(self.ASD_TRAITS) if self.ASD_TRAITS else 0
            
            summary["trait_coverage"] = trait_coverage
            summary["trait_count"] = trait_count
    
    def get_condition_timeline(self) -> List[Dict[str, Any]]:
        """
        Get the chronological timeline of condition mentions.
        
        Returns:
            List of timeline entries
        """
        return self.condition_timeline
    
    def get_comorbidity_analysis(self) -> Dict[str, Any]:
        """
        Analyze comorbidities between tracked conditions.
        
        Returns:
            Dictionary with comorbidity analysis
        """
        # Count documents for each condition
        condition_docs = {}
        for condition in self.condition_mentions:
            condition_docs[condition] = set(
                mention["document"]["id"] for mention in self.condition_mentions[condition]
            )
        
        # Calculate overlap between conditions
        comorbidities = {}
        for condition1 in condition_docs:
            comorbidities[condition1] = {}
            
            for condition2 in condition_docs:
                if condition1 == condition2:
                    continue
                
                overlap = len(condition_docs[condition1].intersection(condition_docs[condition2]))
                
                if overlap > 0:
                    comorbidities[condition1][condition2] = {
                        "shared_documents": overlap,
                        "percentage": overlap / len(condition_docs[condition1]) if condition_docs[condition1] else 0
                    }
        
        # Create clusters of related conditions
        condition_clusters = self._identify_condition_clusters(condition_docs)
        
        return {
            "condition_document_counts": {
                condition: len(docs) for condition, docs in condition_docs.items()
            },
            "comorbidities": comorbidities,
            "condition_clusters": condition_clusters
        }
    
    def _identify_condition_clusters(self, condition_docs: Dict[str, Set[str]]) -> List[List[str]]:
        """
        Identify clusters of related conditions.
        
        Args:
            condition_docs: Dictionary mapping conditions to document sets
            
        Returns:
            List of condition clusters
        """
        # Calculate Jaccard similarity between condition document sets
        similarity_matrix = {}
        for condition1 in condition_docs:
            similarity_matrix[condition1] = {}
            
            for condition2 in condition_docs:
                if condition1 == condition2:
                    similarity_matrix[condition1][condition2] = 1.0
                    continue
                
                intersection = len(condition_docs[condition1].intersection(condition_docs[condition2]))
                union = len(condition_docs[condition1].union(condition_docs[condition2]))
                
                similarity = intersection / union if union > 0 else 0
                similarity_matrix[condition1][condition2] = similarity
        
        # Group conditions with similarity above threshold
        similarity_threshold = 0.3
        clusters = []
        used_conditions = set()
        
        for condition in condition_docs:
            if condition in used_conditions:
                continue
            
            # Find related conditions
            related = [
                c for c in condition_docs 
                if similarity_matrix[condition][c] >= similarity_threshold
            ]
            
            if related:
                clusters.append(related)
                used_conditions.update(related)
        
        # Add any remaining conditions as single-condition clusters
        for condition in condition_docs:
            if condition not in used_conditions:
                clusters.append([condition])
        
        return clusters


# Factory function for easy instantiation
def create_condition_tracker() -> ConditionTracker:
    """
    Create a condition tracker instance.
    
    Returns:
        Configured ConditionTracker instance
    """
    return ConditionTracker() 