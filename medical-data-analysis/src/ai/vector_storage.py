"""
Vector storage module for medical text embeddings.
Provides functionality to store, retrieve, and search embeddings of medical entities.
"""

import json
import logging
import numpy as np
import os
from typing import Dict, List, Any, Union, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle numpy arrays."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class MedicalVectorStore:
    """Store and retrieve vector embeddings for medical entities."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the vector store.
        
        Args:
            storage_dir: Directory to store vector data
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "vector_data")
        self.vectors = {}  # id -> embedding
        self.metadata = {}  # id -> metadata
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Created vector storage directory at {self.storage_dir}")
        
        self.vector_file = os.path.join(self.storage_dir, "vectors.json")
        self.metadata_file = os.path.join(self.storage_dir, "metadata.json")
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load vector and metadata data from disk."""
        try:
            if os.path.exists(self.vector_file):
                with open(self.vector_file, 'r') as f:
                    vector_data = json.load(f)
                    # Convert lists back to numpy arrays
                    self.vectors = {k: np.array(v) for k, v in vector_data.items()}
                logger.info(f"Loaded {len(self.vectors)} vectors from {self.vector_file}")
            
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.metadata)} entities from {self.metadata_file}")
        
        except Exception as e:
            logger.error(f"Error loading vector data: {e}")
            # Initialize empty if loading fails
            self.vectors = {}
            self.metadata = {}
    
    def _save_data(self):
        """Save vector and metadata data to disk."""
        try:
            with open(self.vector_file, 'w') as f:
                json.dump(self.vectors, f, cls=NumpyEncoder)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f)
            
            logger.info(f"Saved {len(self.vectors)} vectors and metadata to disk")
        
        except Exception as e:
            logger.error(f"Error saving vector data: {e}")
    
    def add_entity(self, entity_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """
        Add an entity with its embedding and metadata to the vector store.
        
        Args:
            entity_id: Unique identifier for the entity
            embedding: Vector embedding of the entity
            metadata: Additional information about the entity
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.vectors[entity_id] = embedding
            self.metadata[entity_id] = metadata
            self._save_data()
            return True
        
        except Exception as e:
            logger.error(f"Error adding entity {entity_id}: {e}")
            return False
    
    def store_embedding(self, entity_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> bool:
        """
        Alias for add_entity to ensure method name consistency.
        
        Args:
            entity_id: Unique identifier for the entity
            embedding: Vector embedding of the entity
            metadata: Additional information about the entity
        
        Returns:
            True if successful, False otherwise
        """
        return self.add_entity(entity_id, embedding, metadata)
    
    def add_entities(self, entities: List[Dict[str, Any]]) -> int:
        """
        Add multiple entities to the vector store.
        
        Args:
            entities: List of entity dictionaries, each with id, embedding, and metadata
        
        Returns:
            Number of entities successfully added
        """
        success_count = 0
        for entity in entities:
            if "id" in entity and "embedding" in entity and "metadata" in entity:
                if self.add_entity(entity["id"], entity["embedding"], entity["metadata"]):
                    success_count += 1
        
        return success_count
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
        
        Returns:
            Dictionary with embedding and metadata, or None if not found
        """
        if entity_id in self.vectors and entity_id in self.metadata:
            return {
                "id": entity_id,
                "embedding": self.vectors[entity_id],
                "metadata": self.metadata[entity_id]
            }
        return None
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for entities similar to the query embedding.
        
        Args:
            query_embedding: Vector embedding to compare against
            top_k: Number of top results to return
        
        Returns:
            List of dictionaries with entity information and similarity scores
        """
        if not self.vectors:
            return []
        
        # Calculate similarities
        similarities = []
        for entity_id, embedding in self.vectors.items():
            # Calculate cosine similarity
            similarity = self._calculate_similarity(query_embedding, embedding)
            similarities.append((entity_id, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for entity_id, similarity in similarities[:top_k]:
            results.append({
                "id": entity_id,
                "similarity": similarity,
                "metadata": self.metadata.get(entity_id, {})
            })
        
        return results
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Cosine similarity between the embeddings (between -1 and 1)
        """
        # Normalize the embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        embedding1_normalized = embedding1 / norm1
        embedding2_normalized = embedding2 / norm2
        
        # Calculate cosine similarity
        return float(np.dot(embedding1_normalized, embedding2_normalized))
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for the given text.
        This is a placeholder that should be replaced with your actual embedding code.
        
        Args:
            text: Text to generate embedding for
        
        Returns:
            Vector embedding of the text
        """
        # WARNING: This is just a placeholder for testing
        # In a real implementation, you would use a proper embedding model
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.rand(128)
        return embedding / np.linalg.norm(embedding)
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity from the vector store.
        
        Args:
            entity_id: ID of the entity to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if entity_id in self.vectors:
                del self.vectors[entity_id]
            
            if entity_id in self.metadata:
                del self.metadata[entity_id]
            
            self._save_data()
            return True
        
        except Exception as e:
            logger.error(f"Error deleting entity {entity_id}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all entities from the vector store.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.vectors = {}
            self.metadata = {}
            self._save_data()
            return True
        
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False 