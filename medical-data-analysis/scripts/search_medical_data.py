#!/usr/bin/env python3
"""
Search Medical Data Script

This script uses the vector database to perform semantic searches
across your processed medical documents.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def load_processed_documents() -> List[Dict[str, Any]]:
    """
    Load all processed document embeddings from the extraction directory.
    
    Returns:
        List of document dictionaries with their embeddings
    """
    docs = []
    extraction_dir = Path("processed_data/extracted")
    
    if not extraction_dir.exists():
        extraction_dir = Path("processed_data")  # Fallback location
    
    logger.info(f"Looking for processed documents in {extraction_dir}")
    
    # Load all JSON files from the extraction directory
    for file_path in extraction_dir.glob("**/*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                
                # Check if this document has an embedding
                if 'ai_analysis' in doc and 'embedding' in doc['ai_analysis']:
                    # Add the filename for reference
                    doc['filename'] = file_path.name
                    docs.append(doc)
                    logger.info(f"Loaded document with embedding: {file_path.name}")
                else:
                    # Also look directly in the extraction directory
                    direct_path = Path(f"processed_data/{file_path.stem}_extraction.json")
                    if direct_path.exists():
                        with open(direct_path, 'r', encoding='utf-8') as direct_f:
                            direct_doc = json.load(direct_f)
                            if 'ai_analysis' in direct_doc and 'embedding' in direct_doc['ai_analysis']:
                                direct_doc['filename'] = direct_path.name
                                docs.append(direct_doc)
                                logger.info(f"Loaded document with embedding: {direct_path.name}")
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
    
    logger.info(f"Loaded {len(docs)} documents with embeddings")
    return docs

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    import numpy as np
    
    # Convert to numpy arrays if they aren't already
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0
    
    return dot_product / (norm_a * norm_b)

def get_embedding_for_query(query: str):
    """
    Get embedding for a search query using the same model as for documents.
    
    Args:
        query: Search query text
        
    Returns:
        Embedding vector for the query
    """
    try:
        # Import the embedding module
        from src.ai.embedding import MedicalEmbedding
        
        # Create embedding model
        embedding_model = MedicalEmbedding(model_name="medical-embedding-default")
        
        # Generate embedding for query
        return embedding_model.generate_embedding(query)
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        # Provide a fallback method if the model isn't available
        logger.info("Using fallback random embedding for testing")
        import numpy as np
        return np.random.rand(128).tolist()  # Same dimension as used in the pipeline

def search_documents(query: str, docs: List[Dict[str, Any]], top_n=5):
    """
    Search documents for semantic similarity to the query.
    
    Args:
        query: Search query text
        docs: List of documents with embeddings
        top_n: Number of top results to return
        
    Returns:
        List of top matching documents with similarity scores
    """
    try:
        # Get embedding for the query
        query_embedding = get_embedding_for_query(query)
        
        results = []
        
        # Calculate similarity for each document
        for doc in docs:
            try:
                doc_embedding = doc['ai_analysis']['embedding']
                similarity = cosine_similarity(query_embedding, doc_embedding)
                
                # Create result with document info and similarity score
                result = {
                    'filename': doc['filename'],
                    'similarity': similarity,
                    'metadata': doc.get('metadata', {})
                }
                
                # Add extracted entities if available
                if 'ai_analysis' in doc and 'entities' in doc['ai_analysis']:
                    result['entities'] = doc['ai_analysis']['entities']
                
                # Add any extracted dates
                if 'dates' in doc:
                    result['dates'] = doc['dates']
                
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing document {doc.get('filename', 'unknown')}: {str(e)}")
        
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top N results
        return results[:top_n]
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return []

def main():
    """Main function to search medical documents."""
    # Load all processed documents
    docs = load_processed_documents()
    
    if not docs:
        logger.error("No documents with embeddings found. Make sure to run the data processing first.")
        return 1
    
    # Define some example searches
    example_searches = [
        "chronic pain",
        "neurological symptoms",
        "gastrointestinal issues",
        "hypermobility",
        "rheumatology",
        "lab results",
        "medication side effects",
        "family medical history"
    ]
    
    print("\nMEDICAL DATA SEMANTIC SEARCH")
    print("===========================\n")
    
    # Let the user choose a search query
    print("Example searches:")
    for i, example in enumerate(example_searches):
        print(f"{i+1}. {example}")
    
    print("\nEnter a number to use an example search, or type your own query:")
    user_input = input("> ")
    
    # Process user input
    if user_input.isdigit() and 1 <= int(user_input) <= len(example_searches):
        query = example_searches[int(user_input) - 1]
    else:
        query = user_input
    
    print(f"\nSearching for: '{query}'")
    results = search_documents(query, docs)
    
    # Display results
    if results:
        print(f"\nFound {len(results)} relevant documents:\n")
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result['filename']}")
            print(f"Relevance: {result['similarity']:.4f}")
            
            # Show entity counts if available
            if 'entities' in result:
                print("Entities found:")
                for entity_type, entities in result['entities'].items():
                    if entities:
                        print(f"  {entity_type}: {len(entities)}")
            
            print()
    else:
        print("No matching documents found.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 