"""
Medical Vector Store Module

This module provides specialized vector embedding and retrieval for medical data, 
optimized for EDS, neurodevelopmental conditions, and related medical information.
It supports semantic search across medical documents and entities.
"""

import os
import uuid
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import logging

# Vector embedding libraries
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Import NumpyEncoder from our numpy_json module
from src.ai.vectordb.numpy_json import NumpyEncoder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalVectorStore:
    """
    Vector storage and retrieval system optimized for medical data,
    with specialized embedding strategies for different medical entity types.
    """
    
    def __init__(
        self,
        storage_path: str = "vectordb",
        embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO",
        use_gpu: bool = False,
        dimension_reduction: Optional[int] = None
    ):
        """
        Initialize the medical vector store.
        
        Args:
            storage_path: Path to store vector embeddings
            embedding_model: Name of the sentence transformer model to use
            use_gpu: Whether to use GPU for embedding generation
            dimension_reduction: If set, reduce dimensions to this value
        """
        self.storage_path = str(Path(storage_path))  # Convert to string for proper comparisons
        self.embedding_model_name = embedding_model
        self.dimension_reduction = dimension_reduction
        self.use_gpu = use_gpu
        
        # Create storage directory
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(Path(self.storage_path) / "entities", exist_ok=True)
        os.makedirs(Path(self.storage_path) / "documents", exist_ok=True)
        
        # Load index file if it exists
        self.index_path = Path(self.storage_path) / "index.json"
        self.load_index()
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        self.entities = {}  # In-memory store for entities and their embeddings
        self.documents = {}  # In-memory store for documents and their embeddings
        self._load_data()
        logger.info(f"Initialized MedicalVectorStore at {storage_path}")
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model."""
        try:
            device = "cuda" if self.use_gpu else "cpu"
            self.embedding_model = SentenceTransformer(self.embedding_model_name, device=device)
            logger.info(f"Initialized embedding model {self.embedding_model_name} on {device}")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            raise
    
    def load_index(self):
        """Load the vector store index from disk."""
        try:
            index_path = Path(self.storage_path) / "index.json"
            if index_path.exists():
                with open(index_path, 'r') as f:
                    self.index = json.load(f)
            else:
                # Initialize empty index
                self.index = {
                    "documents": {},
                    "conditions": {},
                    "symptoms": {},
                    "medications": {},
                    "procedures": {},
                    "lab_results": {},
                    "other": {}
                }
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            # Initialize empty index
            self.index = {
                "documents": {},
                "conditions": {},
                "symptoms": {},
                "medications": {},
                "procedures": {},
                "lab_results": {},
                "other": {}
            }
    
    def save_index(self):
        """Save the vector store index to disk."""
        try:
            index_path = Path(self.storage_path) / "index.json"
            with open(index_path, 'w') as f:
                json.dump(self.index, f, cls=NumpyEncoder)
            logger.info(f"Saved vector index with {sum(len(entities) for entities in self.index.values())} entries")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Numpy array containing the embedding vector
        """
        # Truncate extremely long text to prevent memory issues
        max_length = 10000  # Approximate max length
        if len(text) > max_length:
            # Try to truncate at paragraph boundaries
            paragraphs = text.split('\n\n')
            truncated_text = ""
            for para in paragraphs:
                if len(truncated_text) + len(para) + 2 <= max_length:
                    if truncated_text:
                        truncated_text += "\n\n" + para
                    else:
                        truncated_text = para
                else:
                    break
            text = truncated_text
        
        # Generate embedding
        embedding = self.embedding_model.encode(text, show_progress_bar=False)
        
        # Apply dimension reduction if specified
        if self.dimension_reduction and embedding.shape[0] > self.dimension_reduction:
            # Simple random projection for dimension reduction
            projection_matrix = np.random.normal(size=(embedding.shape[0], self.dimension_reduction))
            # Normalize columns
            projection_matrix = projection_matrix / np.sqrt(np.sum(projection_matrix**2, axis=0))
            embedding = np.dot(embedding, projection_matrix)
        
        return np.array(embedding)  # Ensure return type is np.ndarray
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Alias for generate_embedding to maintain consistent API with other components.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Numpy array containing the embedding vector
        """
        return self.generate_embedding(text)
    
    def add_document(self, document_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a document with its embedding to the vector store.
        
        Args:
            document_id: Unique identifier for the document
            text: Document text
            metadata: Optional metadata for the document
            
        Returns:
            Document ID
        """
        metadata = metadata or {}  # Use empty dict instead of None
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Create document data structure
            document_data = {
                "text": text,
                "metadata": metadata,
                "embedding": embedding.tolist()  # Convert to list for JSON serialization
            }
            
            # Store in memory
            self.documents[document_id] = document_data
            
            # Ensure directories exist
            storage_path = Path(self.storage_path)
            doc_dir = storage_path / "documents"
            os.makedirs(doc_dir, exist_ok=True)
            
            # Save document to disk
            vector_id = f"vector_{document_id}"
            vector_path = storage_path / f"{vector_id}.npy"
            doc_path = doc_dir / f"{document_id}.json"
            
            # Save vector as numpy file
            np.save(vector_path, embedding)
            
            # Save document JSON
            with open(doc_path, 'w') as f:
                json.dump(document_data, f, cls=NumpyEncoder)
            
            # Update index
            self.index["documents"][document_id] = {
                "id": document_id,
                "vector_path": str(vector_path),
                "doc_path": str(doc_path),
                "metadata": metadata
            }
            self.save_index()
            
            return document_id
        
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise
            
    def add_medical_entity(
        self, 
        entity_id: str,
        text: str,
        entity_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a medical entity with its embedding to the vector store.
        
        Args:
            entity_id: Unique identifier for the entity
            text: Entity text
            entity_type: Type of entity (condition, symptom, medication, procedure, lab_result)
            metadata: Optional metadata for the entity
            
        Returns:
            Entity ID
        """
        metadata = metadata or {}  # Use empty dict instead of None
        
        # Normalize entity type
        entity_type = entity_type.lower()
        
        # Map singular to plural forms for storage categories
        type_mapping = {
            'condition': 'conditions',
            'symptom': 'symptoms',
            'medication': 'medications',
            'procedure': 'procedures',
            'lab_result': 'lab_results',
            'conditions': 'conditions',
            'symptoms': 'symptoms',
            'medications': 'medications',
            'procedures': 'procedures',
            'lab_results': 'lab_results'
        }
        
        # Get the storage category for this entity type
        if entity_type in type_mapping:
            storage_type = type_mapping[entity_type]
        else:
            valid_types = list(type_mapping.keys())
            raise ValueError(f"Invalid entity type: {entity_type}. Must be one of {valid_types}")
        
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Create entity data structure
            entity_data = {
                "id": entity_id,
                "text": text,
                "type": entity_type,
                "metadata": metadata,
                "embedding": embedding.tolist()  # Convert to list for JSON serialization
            }
            
            # Store in memory
            self.entities[entity_id] = entity_data
            
            # Ensure directories exist
            storage_path = Path(self.storage_path)
            entity_dir = storage_path / "entities"
            os.makedirs(entity_dir, exist_ok=True)
            
            # Save entity to disk
            entity_path = entity_dir / f"{entity_id}.json"
            
            # Save entity JSON
            with open(entity_path, 'w') as f:
                json.dump(entity_data, f, cls=NumpyEncoder)
            
            # Update index
            self.index[storage_type][entity_id] = {
                "id": entity_id,
                "vector_path": str(entity_path),
                "metadata": metadata
            }
            self.save_index()
            
            return entity_id
        
        except Exception as e:
            logger.error(f"Error adding entity: {str(e)}")
            raise
            
    def add_entity(
        self, 
        entity_id: str,
        text: str,
        entity_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Alias for add_medical_entity for backwards compatibility.
        
        Args:
            entity_id: Unique identifier for the entity
            text: Entity text
            entity_type: Type of entity (condition, symptom, medication, etc.)
            metadata: Optional metadata for the entity
            
        Returns:
            Entity ID
        """
        metadata = metadata or {}  # Use empty dict instead of None
        return self.add_medical_entity(entity_id, text, entity_type, metadata)
        
    def store_embedding(
        self, 
        entity_id: str,
        text: str,
        entity_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Alias for add_entity to maintain consistent naming across the codebase.
        
        Args:
            entity_id: Unique identifier for the entity
            text: Entity text
            entity_type: Type of entity (condition, symptom, medication, etc.)
            metadata: Optional metadata for the entity
            
        Returns:
            Entity ID
        """
        metadata = metadata or {}  # Use empty dict instead of None
        return self.add_entity(entity_id, text, entity_type, metadata)
    
    def search(self, query_text: str, entity_types: Optional[List[str]] = None, limit: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for documents or entities similar to the query text.
        
        Args:
            query_text: Query text to search for
            entity_types: Optional list of entity types to search in, e.g., ['conditions', 'medications'] or ['condition', 'medication']
            limit: Maximum number of results to return
            threshold: Minimum similarity score to include in results (0.0 to 1.0)
            
        Returns:
            List of dictionaries with search results
        """
        entity_types = entity_types or ["documents"]  # Use empty list instead of None
        
        # Generate embedding for query
        query_embedding = self.generate_embedding(text=query_text)
        
        # Prepare results container
        results = []
        
        # Entity type mapping from singular to plural
        entity_type_mapping = {
            "document": "documents",
            "condition": "conditions",
            "symptom": "symptoms",
            "medication": "medications",
            "procedure": "procedures",
            "lab_result": "lab_results",
        }
        
        # Process entity types to ensure they use the plural form
        processed_entity_types = []
        for entity_type in entity_types:
            # Convert to lowercase for case-insensitive matching
            entity_type = entity_type.lower()
            # Map singular to plural if needed
            if entity_type in entity_type_mapping:
                processed_entity_types.append(entity_type_mapping[entity_type])
            else:
                # If it's already plural or not in our mapping, keep it as is
                processed_entity_types.append(entity_type)
        
        # Search in each requested entity type
        for entity_type in processed_entity_types:
            # Ensure it's a valid type
            if entity_type not in self.index:
                logger.warning(f"Unknown entity type '{entity_type}', skipping")
                continue
                
            # Search for entities of this type
            if entity_type == "documents":
                # Search in documents
                for doc_id, doc_data in self.documents.items():
                    if "embedding" in doc_data:
                        # Convert list to np.array for cosine_similarity
                        doc_embedding = np.array(doc_data["embedding"]).reshape(1, -1)
                        query_embedding_reshaped = query_embedding.reshape(1, -1)
                        similarity = cosine_similarity(query_embedding_reshaped, doc_embedding)[0][0]
                        if similarity >= threshold:
                            results.append({
                                "id": doc_id,
                                "text": doc_data.get("text", ""),
                                "metadata": doc_data.get("metadata", {}),
                                "similarity": float(similarity),
                                "entity_type": "document"
                            })
            else:
                # Search in entities
                entity_type_singular = entity_type.rstrip('s')
                for entity_id, entity_data in self.entities.items():
                    # Check if entity belongs to the requested type
                    entity_type_value = entity_data.get("type", "").lower()
                    entity_metadata = entity_data.get("metadata", {})
                    metadata_entity_type = entity_metadata.get("entity_type", "").lower()
                    
                    # Match if either the direct type field matches or the metadata field matches
                    if (entity_type_singular == entity_type_value or 
                        entity_type_singular == metadata_entity_type):
                        if "embedding" in entity_data:
                            # Convert list to np.array for cosine_similarity
                            entity_embedding = np.array(entity_data["embedding"]).reshape(1, -1)
                            query_embedding_reshaped = query_embedding.reshape(1, -1)
                            similarity = cosine_similarity(query_embedding_reshaped, entity_embedding)[0][0]
                            if similarity >= threshold:
                                # Use the type from the entity data if available, otherwise from metadata
                                final_entity_type = entity_type_value or metadata_entity_type
                                results.append({
                                    "id": entity_id,
                                    "text": entity_data.get("text", ""),
                                    "metadata": entity_metadata,
                                    "similarity": float(similarity),
                                    "entity_type": final_entity_type
                                })
        
        # Sort results by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return limited results
        return results[:limit]
    
    def delete_entity(self, entity_type: str, entity_id: str) -> int:
        """
        Delete an entity from the vector store.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity to delete
            
        Returns:
            Number of vectors deleted
        """
        if entity_type not in self.index:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        # Find vectors to delete
        to_delete = []
        id_field = "entity_id" if entity_type != "documents" else "document_id"
        
        for vector_id, entry in self.index[entity_type].items():
            if entry.get(id_field) == entity_id:
                to_delete.append(vector_id)
        
        # Delete vectors
        for vector_id in to_delete:
            # Delete vector file
            vector_path = self.index[entity_type][vector_id]["vector_path"]
            try:
                if os.path.exists(vector_path):
                    os.remove(vector_path)
            except Exception as e:
                logger.error(f"Error deleting vector file {vector_path}: {e}")
            
            # Remove from index
            del self.index[entity_type][vector_id]
        
        # Save index
        self.save_index()
        
        return len(to_delete)
    
    def get_similar_conditions(self, condition_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find conditions similar to the given condition text.
        
        Args:
            condition_text: Text describing the condition
            limit: Maximum number of results to return
            
        Returns:
            List of similar conditions with similarity scores
        """
        return self.search(condition_text, entity_types=["conditions"], limit=limit)
    
    def get_similar_symptoms(self, symptom_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find symptoms similar to the given symptom text.
        
        Args:
            symptom_text: Text describing the symptom
            limit: Maximum number of results to return
            
        Returns:
            List of similar symptoms with similarity scores
        """
        return self.search(symptom_text, entity_types=["symptoms"], limit=limit)
    
    def find_related_documents(self, entity_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents related to the given entity text.
        
        Args:
            entity_text: Text describing the entity
            limit: Maximum number of results to return
            
        Returns:
            List of related documents with similarity scores
        """
        return self.search(entity_text, entity_types=["documents"], limit=limit)
    
    def find_related_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find entities related to the given text, grouped by entity type.
        
        Args:
            text: Text to find related entities for
            entity_types: List of entity types to search, or None for all
            limit: Maximum number of results to return per entity type
            
        Returns:
            Dictionary of entity type to list of related entities
        """
        if entity_types is None:
            entity_types = ["conditions", "symptoms", "medications", "procedures", "lab_results"]
        
        # Get overall results
        results = self.search(text, entity_types=entity_types, limit=limit * len(entity_types))
        
        # Group by entity type
        grouped_results = {}
        for entity_type in entity_types:
            grouped_results[entity_type] = []
        
        for result in results:
            entity_type = result["entity_type"]
            if entity_type in grouped_results and len(grouped_results[entity_type]) < limit:
                grouped_results[entity_type].append(result)
        
        return grouped_results
    
    def _load_data(self):
        """Load documents and entities from disk."""
        # Load documents
        try:
            entity_dir = Path(self.storage_path) / "entities"
            document_dir = Path(self.storage_path) / "documents"
            
            # Load documents
            if document_dir.exists():
                for file_path in document_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            document_data = json.load(f)
                            document_id = file_path.stem
                            self.documents[document_id] = document_data
                    except Exception as e:
                        logger.error(f"Error loading document {file_path}: {str(e)}")
            
            # Load entities
            if entity_dir.exists():
                for file_path in entity_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            entity_data = json.load(f)
                            entity_id = file_path.stem
                            self.entities[entity_id] = entity_data
                    except Exception as e:
                        logger.error(f"Error loading entity {file_path}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error loading vector data: {str(e)}")
    
    def store_document(self, text: str, metadata: Optional[dict] = None) -> str:
        """Store a document in the vector database.
        
        This is an alias for add_document to match test expectations.
        
        Args:
            text: The document text
            metadata: Optional metadata dictionary
            
        Returns:
            Document ID
        """
        metadata = metadata or {}  # Use empty dict instead of None
        document_id = f"doc_{uuid.uuid4()}"
        return self.add_document(document_id, text, metadata)
    
    def store_entity(self, entity: Dict[str, Any]) -> str:
        """Store an entity in the vector database.
        
        This is an alias for add_entity to match test expectations.
        
        Args:
            entity: The entity to store
            
        Returns:
            Entity ID
        """
        entity_id = f"entity_{uuid.uuid4()}"
        entity_type = entity.get("type", "unknown")
        text = entity.get("text", "")
        metadata = entity.get("metadata", {})
        
        # Add entity_type to metadata to ensure it can be found in searches
        metadata["entity_type"] = entity_type
        
        return self.add_entity(entity_id, text, entity_type, metadata)
    
    def cleanup(self):
        """
        Clean up the vector store by removing all vectors.
        """
        try:
            # Clear in-memory data
            self.entities = {}
            self.documents = {}
            
            # Reset index
            self.index = {
                "documents": {},
                "conditions": {},
                "symptoms": {},
                "medications": {},
                "procedures": {},
                "lab_results": {},
                "other": {}
            }
            self.save_index()
            
            # Remove files
            import shutil
            storage_path = Path(self.storage_path) if isinstance(self.storage_path, str) else self.storage_path
            for subdir in ["entities", "documents"]:
                dir_path = storage_path / subdir
                if dir_path.exists():
                    for file_path in dir_path.glob("*.json"):
                        file_path.unlink()
            
            logger.info("Vector store cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up vector store: {str(e)}")
            raise
    
    def search_similar_entities(self, query_text: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """Search for entities similar to the query text.
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            
        Returns:
            List of (entity_id, entity_data, similarity_score) tuples
        """
        if not self.entities:
            return []
        
        query_embedding = self.generate_embedding(query_text)
        results = []
        
        for entity_id, entity_data in self.entities.items():
            if "embedding" not in entity_data or entity_data["embedding"] is None:
                continue
                
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, entity_data["embedding"])
            results.append((entity_id, entity_data, similarity))
        
        # Sort by similarity (highest first) and take top k
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]
    
    def search_similar_documents(self, query_text: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """Search for documents similar to the query text.
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            
        Returns:
            List of (document_id, document_data, similarity_score) tuples
        """
        if not self.documents:
            return []
        
        query_embedding = self.generate_embedding(query_text)
        results = []
        
        for doc_id, doc_data in self.documents.items():
            if "embedding" not in doc_data or doc_data["embedding"] is None:
                continue
                
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, doc_data["embedding"])
            results.append((doc_id, doc_data, similarity))
        
        # Sort by similarity (highest first) and take top k
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Entity data or None if not found
        """
        return self.entities.get(entity_id)
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            Document data or None if not found
        """
        return self.documents.get(document_id)
    
    def close(self):
        """
        Close the vector store and save any pending changes.
        
        This method ensures all data is properly saved before shutting down.
        """
        try:
            # Save the index
            self.save_index()
            
            # Clear in-memory data
            self.documents = {}
            self.entities = {}
            
            logger.info(f"Closed vector store at {self.storage_path}")
        except Exception as e:
            logger.error(f"Error closing vector store: {str(e)}")
            raise 