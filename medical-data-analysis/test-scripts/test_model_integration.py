#!/usr/bin/env python
"""
Test script to verify successful integration with Hugging Face models.
This script attempts to initialize each AI component and reports whether
the models were loaded successfully.
"""

import os
import sys
from datetime import datetime
import pytest
from src.ai.model_integration import ModelIntegration
from unittest.mock import Mock, patch

# Import AI components
from src.ai.entity_extraction import MedicalEntityExtractor
from src.ai.text_analysis import MedicalTextAnalyzer
from src.ai.embedding import MedicalEmbedding
from src.ai.rag import MedicalRAG

@pytest.fixture
def entity_extractor():
    return MedicalEntityExtractor()

@pytest.fixture
def text_analyzer():
    return MedicalTextAnalyzer()

@pytest.fixture
def model_integration():
    return ModelIntegration()

def run_model_integration_test():
    """Test if Hugging Face models are loading correctly."""
    print("=" * 50)
    print("TESTING HUGGING FACE MODEL INTEGRATION")
    print("=" * 50)
    
    # Sample text for testing
    sample_text = """
    Patient has hypermobility in multiple joints with a Beighton score of 8/9. 
    They experience chronic joint pain and have been diagnosed with Ehlers-Danlos Syndrome.
    Currently taking 50mg of tramadol for pain management.
    """
    
    # Test Entity Extraction
    print("\nTesting Medical Entity Extractor...")
    entity_extractor = MedicalEntityExtractor(use_transformer_models=True)
    
    if entity_extractor.models_loaded:
        print("✅ Entity extraction model loaded successfully")
        entities = entity_extractor.extract_entities(sample_text)
        print(f"  Extracted {len(entities['conditions'])} conditions")
        print(f"  Extracted {len(entities['medications'])} medications")
        print(f"  Extracted {len(entities['symptoms'])} symptoms")
    else:
        print("❌ Entity extraction model NOT loaded")
    
    # Test Text Analysis
    print("\nTesting Medical Text Analyzer...")
    text_analyzer = MedicalTextAnalyzer(use_transformer_models=True)
    
    if text_analyzer.models_loaded:
        print("✅ Text analysis models loaded successfully")
        analysis = text_analyzer.analyze_text(sample_text)
        print(f"  Extracted {len(analysis['concepts'])} concepts")
        print(f"  Detected {len(analysis['negation'])} negations")
    else:
        print("❌ Text analysis models NOT loaded")
    
    # Test Embedding
    print("\nTesting Medical Embedding...")
    embedding_model = MedicalEmbedding()  # Explicitly use CPU
    
    if embedding_model.model is not None:
        print("✅ Embedding model loaded successfully")
        embedding = embedding_model.embed_text(sample_text)
        print(f"  Generated embedding with dimension {embedding.shape}")
    else:
        print("❌ Embedding model NOT loaded")
    
    # Test RAG
    print("\nTesting Medical RAG...")
    rag_model = MedicalRAG()
    
    if rag_model.models_loaded:
        print("✅ RAG models loaded successfully")
        similar_docs = rag_model.find_similar_medical_records(sample_text)
        print(f"  Found {len(similar_docs)} similar documents")
    else:
        print("❌ RAG models NOT loaded")
    
    # Print summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"Entity Extraction: {'✅ LOADED' if entity_extractor.models_loaded else '❌ NOT LOADED'}")
    print(f"Text Analysis: {'✅ LOADED' if text_analyzer.models_loaded else '❌ NOT LOADED'}")
    print(f"Embedding: {'✅ LOADED' if embedding_model.model is not None else '❌ NOT LOADED'}")
    print(f"Rag: {'✅ LOADED' if rag_model.models_loaded else '❌ NOT LOADED'}")
    
    # Overall status
    all_loaded = all([
        entity_extractor.models_loaded,
        text_analyzer.models_loaded,
        embedding_model.model is not None,
        rag_model.models_loaded
    ])
    
    some_loaded = any([
        entity_extractor.models_loaded,
        text_analyzer.models_loaded,
        embedding_model.model is not None,
        rag_model.models_loaded
    ])
    
    if all_loaded:
        print("\nOVERALL STATUS:")
        print("✅ All models loaded successfully")
    elif some_loaded:
        print("\nOVERALL STATUS:")
        print("⚠️ Partial integration - some models loaded, others using fallbacks")
    else:
        print("\nOVERALL STATUS:")
        print("❌ No models loaded - using rule-based fallbacks")

def test_entity_extraction(entity_extractor):
    test_text = """
    Patient presents with chronic joint pain and fatigue.
    Currently taking Lyrica 75mg BID for pain management.
    History of EDS and POTS.
    """
    
    result = entity_extractor.extract_entities(test_text)
    
    assert "conditions" in result
    assert "medications" in result
    assert "symptoms" in result
    assert any(entity["name"].lower() == "pain" for entity in result["symptoms"])
    assert any(entity["name"] == "Lyrica" for entity in result["medications"])

def test_text_analysis(text_analyzer):
    test_text = "Patient shows improvement in joint stability. Pain levels decreased."
    
    result = text_analyzer.analyze_text(test_text)
    
    assert "sentiment" in result
    assert "topics" in result
    assert result["sentiment"]["positive"] > result["sentiment"]["negative"]
    assert "rheumatology" in result["topics"]

def test_model_integration_func(model_integration):
    test_text = """
    Follow-up visit for EDS management.
    Patient reports reduced pain with current medication regimen.
    Continues physical therapy exercises as prescribed.
    """
    
    result = model_integration.process_text(test_text)
    
    assert "entities" in result
    assert "analysis" in result
    assert "embeddings" in result
    assert "medical_events" in result

if __name__ == "__main__":
    run_model_integration_test() 