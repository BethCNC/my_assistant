#!/usr/bin/env python3
"""
Test AI Integration with Medical Data Processing Pipeline

This script tests the AI components integration with the medical data processing pipeline.
It processes a sample medical text and shows the AI analysis results.
"""

import os
import sys
import logging
import traceback
from pathlib import Path
import json
from datetime import datetime
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure directories
os.makedirs("processed_data", exist_ok=True)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle dates and non-serializable objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

def test_entity_extraction():
    """Test the entity extraction capabilities of the AI integration."""
    try:
        from src.ai.entity_extraction import MedicalEntityExtractor
        
        logger.info("Testing entity extraction...")
        
        # Create a sample medical text
        sample_text = """
        Patient diagnosed with hypermobile Ehlers-Danlos Syndrome (hEDS) in 2018.
        Presents with chronic joint pain, particularly in shoulders, hips, and fingers.
        Reports frequent subluxations and dislocations.
        
        Current medications include:
        - Tramadol 50mg twice daily for pain
        - Cymbalta 60mg daily for pain and mood
        - Vitamin D 2000 IU daily
        
        Recent tests show slightly elevated inflammatory markers. 
        ESR 22 mm/hr (normal range 0-20)
        CRP 2.4 mg/L (normal range 0-1.0)
        
        Also diagnosed with POTS in 2019 after positive tilt table test.
        Reports sensory sensitivities consistent with Autism Spectrum Disorder.
        """
        
        # Initialize the entity extractor
        extractor = MedicalEntityExtractor(use_transformer_models=False)  # Use rule-based for speed and reliability
        
        # Extract entities
        entities = extractor.extract_entities(sample_text)
        
        # Display extracted entities
        logger.info(f"Found {sum(len(v) for v in entities.values())} entities:")
        for entity_type, entity_list in entities.items():
            logger.info(f"- {entity_type}: {len(entity_list)}")
            for i, entity in enumerate(entity_list[:5]):  # Show first 5 of each type
                logger.info(f"  {i+1}. {entity.get('name', entity.get('text', ''))}")
        
        # Save extraction results
        with open("processed_data/entity_extraction_test.json", "w") as f:
            json.dump(entities, f, indent=2, cls=CustomJSONEncoder)
            
        logger.info("Entity extraction test successful")
        return True
    except Exception as e:
        logger.error(f"Error testing entity extraction: {e}")
        logger.error(traceback.format_exc())
        return False

def test_text_analysis():
    """Test the text analysis capabilities of the AI integration."""
    try:
        from src.ai.text_analysis import MedicalTextAnalyzer
        
        logger.info("Testing text analysis...")
        
        # Create a sample medical text
        sample_text = """
        Patient shows improvement in joint stability following 6 weeks of physical therapy.
        Reports reduced pain levels (6/10 down from 8/10) and fewer subluxation events.
        Still experiencing significant fatigue, especially after physical exertion.
        
        Sleep quality remains poor, with frequent awakenings and difficulty maintaining sleep.
        Patient is compliant with medication regimen and reports no significant side effects.
        Mood has improved with current antidepressant dosage.
        
        Recommended continued physical therapy twice weekly, focusing on joint stabilization
        exercises and gradual cardiovascular conditioning. Patient agrees to try melatonin
        2mg at bedtime for sleep difficulties.
        """
        
        # Initialize the text analyzer
        analyzer = MedicalTextAnalyzer()
        
        # Analyze text
        analysis = analyzer.analyze_text(sample_text)
        
        # Display analysis results
        logger.info("Text analysis results:")
        logger.info(f"- Sentiment: {analysis.get('sentiment', {})}")
        logger.info(f"- Topics: {analysis.get('topics', [])}")
        logger.info(f"- Clinical impression: {analysis.get('clinical_impression', '')}")
        
        # Save analysis results
        with open("processed_data/text_analysis_test.json", "w") as f:
            json.dump(analysis, f, indent=2, cls=CustomJSONEncoder)
            
        logger.info("Text analysis test successful")
        return True
    except Exception as e:
        logger.error(f"Error testing text analysis: {e}")
        logger.error(traceback.format_exc())
        return False

def test_pipeline_integration():
    """Test the AI integration with the pipeline."""
    try:
        from src.pipeline.ingestion_pipeline import IngestionPipeline
        from src.ai.model_integration import MedicalAIIntegration
        import tempfile
        import os
        
        logger.info("Testing AI integration with pipeline...")
        
        # Create a sample document content
        sample_content = """
        Dr. Sarah Johnson, MD
        Rheumatology Consultation
        Date: 2025-04-30
        
        Patient: Jane Doe
        DOB: 1985-02-15
        
        HISTORY:
        Patient presents with a history of joint hypermobility and chronic pain. 
        Previous diagnosis of Ehlers-Danlos Syndrome (hEDS) confirmed by geneticist.
        Also diagnosed with Autism Spectrum Disorder in 2023.
        Recent tilt table test confirmed POTS.
        
        MEDICATIONS:
        Tramadol 50mg as needed for pain
        
        ASSESSMENT:
        Patient shows clinical symptoms consistent with hypermobility EDS.
        """
        
        # Save sample content to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_content)
            temp_file_path = f.name
        
        # Initialize pipeline
        pipeline = IngestionPipeline()
        
        # Initialize AI model integration
        # Using a Mock session for testing
        class MockSession:
            def query(self, *args):
                return self
            def filter(self, *args):
                return self
            def first(self):
                return None
                
        integration = MedicalAIIntegration(MockSession())
        
        # Register the AI integration object as a post-processor
        pipeline.register_post_processor(integration.process)
        
        logger.info("✓ AI model integration registered with pipeline")
        
        # Process the test file
        logger.info(f"Processing test document with AI integration: {temp_file_path}")
        result = pipeline.process_file(temp_file_path)
        
        # Check if the AI analysis is in the results
        if "ai_analysis" not in result:
            logger.error("✗ AI analysis not found in processed document")
            logger.error(f"Result keys: {result.keys()}")
            return False
            
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline integration test error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all AI integration tests."""
    logger.info("=== Testing AI Integration Components ===")
    
    test_results = {
        "entity_extraction": test_entity_extraction(),
        "text_analysis": test_text_analysis(),
        "pipeline_integration": test_pipeline_integration()
    }
    
    # Report overall results
    logger.info("\n=== AI Integration Test Results ===")
    all_passed = all(test_results.values())
    
    for test_name, result in test_results.items():
        logger.info(f"{test_name}: {'✓ PASSED' if result else '✗ FAILED'}")
    
    if all_passed:
        logger.info("=== All AI Integration Tests PASSED ===")
        return 0
    else:
        logger.error("=== Some AI Integration Tests FAILED ===")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 