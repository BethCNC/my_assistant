"""
Test Configuration

This module provides test constants, fixtures, and helper functions for testing
the medical data processing pipeline.
"""

import os
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Test constants
SAMPLE_MEDICAL_TEXTS = {
    "eds": """
    Patient diagnosed with hypermobile Ehlers-Danlos Syndrome (hEDS) in 2020.
    Reports chronic joint pain and fatigue. Currently receiving physical therapy.
    Beighton score of 7/9. Joint hypermobility affects knees, elbows, and fingers.
    """,
    
    "asd": """
    Patient evaluated for autism spectrum disorder. Demonstrates restricted interests
    and repetitive behaviors. Social communication difficulties noted in early childhood.
    Currently using visual schedules and social stories as support strategies.
    """,
    
    "comorbid": """
    Patient presents with multiple comorbid conditions including POTS, MCAS, and hEDS.
    Symptoms include tachycardia upon standing, skin flushing, and joint hypermobility.
    Currently managed with compression garments, antihistamines, and physical therapy.
    """
}

SAMPLE_MEDICAL_ENTITIES = {
    "conditions": [
        {
            "type": "condition",
            "text": "Ehlers-Danlos Syndrome",
            "start": 0,
            "end": 22,
            "metadata": {
                "certainty": "confirmed",
                "subtype": "hypermobile"
            }
        },
        {
            "type": "condition",
            "text": "POTS",
            "start": 0,
            "end": 4,
            "metadata": {
                "certainty": "confirmed"
            }
        },
        {
            "type": "condition",
            "text": "autism spectrum disorder",
            "start": 0,
            "end": 24,
            "metadata": {
                "certainty": "evaluation"
            }
        }
    ],
    
    "symptoms": [
        {
            "type": "symptom",
            "text": "joint pain",
            "start": 0,
            "end": 10,
            "metadata": {
                "severity": "chronic",
                "body_part": "general"
            }
        },
        {
            "type": "symptom",
            "text": "fatigue",
            "start": 0,
            "end": 7,
            "metadata": {
                "severity": "moderate"
            }
        },
        {
            "type": "symptom",
            "text": "joint hypermobility",
            "start": 0,
            "end": 18,
            "metadata": {
                "body_part": "knees, elbows, fingers"
            }
        }
    ],
    
    "treatments": [
        {
            "type": "treatment",
            "text": "physical therapy",
            "start": 0,
            "end": 16,
            "metadata": {
                "frequency": "weekly"
            }
        },
        {
            "type": "treatment",
            "text": "compression garments",
            "start": 0,
            "end": 20,
            "metadata": {
                "body_part": "lower extremities"
            }
        }
    ]
}

# Test helpers
def create_temp_test_dir() -> Path:
    """Create a temporary directory for testing."""
    return Path(tempfile.mkdtemp())

def create_test_file(directory: Path, filename: str, content: str) -> Path:
    """Create a test file with the specified content."""
    file_path = directory / filename
    with open(file_path, "w") as f:
        f.write(content)
    return file_path

def create_test_json_file(directory: Path, filename: str, data: Dict) -> Path:
    """Create a JSON test file with the specified data."""
    file_path = directory / filename
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    return file_path

def setup_test_directory_structure(base_dir: Path) -> Dict[str, Path]:
    """Set up a test directory structure for pipeline testing."""
    # Create main directories
    input_dir = base_dir / "input"
    output_dir = base_dir / "processed_data"
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    text_dir = input_dir / "text"
    pdf_dir = input_dir / "pdf"
    html_dir = input_dir / "html"
    
    text_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    html_dir.mkdir(exist_ok=True)
    
    # Create output subdirectories
    (output_dir / "extracted").mkdir(exist_ok=True)
    (output_dir / "processed").mkdir(exist_ok=True)
    (output_dir / "analyzed").mkdir(exist_ok=True)
    (output_dir / "file_registry").mkdir(exist_ok=True)
    
    # Return directory structure
    return {
        "base": base_dir,
        "input": input_dir,
        "output": output_dir,
        "text_input": text_dir,
        "pdf_input": pdf_dir,
        "html_input": html_dir
    }

def create_sample_medical_files(dirs: Dict[str, Path]) -> Dict[str, Path]:
    """Create sample medical files for testing."""
    files = {}
    
    # Create text files
    files["eds_text"] = create_test_file(
        dirs["text_input"], 
        "patient_eds_report.txt",
        SAMPLE_MEDICAL_TEXTS["eds"]
    )
    
    files["asd_text"] = create_test_file(
        dirs["text_input"], 
        "patient_asd_evaluation.txt",
        SAMPLE_MEDICAL_TEXTS["asd"]
    )
    
    files["comorbid_text"] = create_test_file(
        dirs["text_input"], 
        "patient_comorbid_conditions.txt",
        SAMPLE_MEDICAL_TEXTS["comorbid"]
    )
    
    # Create JSON file with medical entities
    files["entities_json"] = create_test_json_file(
        dirs["base"],
        "sample_medical_entities.json",
        SAMPLE_MEDICAL_ENTITIES
    )
    
    return files

def cleanup_test_dir(directory: Path) -> None:
    """Recursively remove a test directory and all contents."""
    import shutil
    if directory.exists():
        shutil.rmtree(directory)

def mock_extraction_result(text: str, file_path: str) -> Dict[str, Any]:
    """Create a mock extraction result for testing."""
    return {
        "content": text,
        "metadata": {
            "file_path": file_path,
            "extraction_time": "2023-06-15T10:30:00Z",
            "file_type": "text/plain"
        }
    }

def mock_ai_analysis_result(text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a mock AI analysis result for testing."""
    return {
        "content": text,
        "metadata": {
            "analysis_time": "2023-06-15T10:35:00Z",
            "model_version": "test-model-v1"
        },
        "ai_analysis": {
            "entities": entities,
            "sentiment": "neutral",
            "summary": "Medical report containing condition and symptom information."
        }
    } 