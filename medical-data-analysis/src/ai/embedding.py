"""
Medical Embedding Module.

Provides tools for generating vector representations of medical text
that can be used for similarity search, clustering, and retrieval.
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from transformers import logging as hf_logging
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce verbosity of transformers warnings
hf_logging.set_verbosity_error()

class MedicalEmbedding:
    """
    Generator for vector embeddings of medical text, optimized for
    medical terminology and context.
    """
    
    def __init__(self, model_name: str = "default-medical-embedding", dimension: int = 128):
        """
        Initialize the medical text embedding generator.
        
        Args:
            model_name: Name of the model to use for embeddings
            dimension: Dimension of the embeddings to generate
        """
        self.model_name = model_name
        self.dimension = dimension
        logger.info(f"Initializing Medical Embedding model {model_name} with dimension {dimension}")
        
        # In a real implementation, we would load the actual model here
        # For testing, we'll use random embeddings
        self.model = None
        
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for the given text.
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            Numpy array of embeddings with shape (n_texts, dimension)
        """
        if not text:
            if isinstance(text, list):
                return np.zeros((0, self.dimension))
            return np.zeros(self.dimension)
        
        try:
            # For testing purposes, generate deterministic random embeddings
            if isinstance(text, list):
                # Process a batch of texts
                embeddings = np.zeros((len(text), self.dimension))
                for i, t in enumerate(text):
                    # Use hash of text for reproducible random seed
                    np.random.seed(hash(t) % 2**32)
                    embeddings[i] = np.random.randn(self.dimension)
                    # Normalize the embedding
                    embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])
                return embeddings
            else:
                # Process a single text
                np.random.seed(hash(text) % 2**32)
                embedding = np.random.randn(self.dimension)
                # Normalize the embedding
                return embedding / np.linalg.norm(embedding)
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            if isinstance(text, list):
                return np.zeros((len(text), self.dimension))
            return np.zeros(self.dimension)
    
    def generate_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Alias for embed_text for backward compatibility.
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        return self.embed_text(text)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity between the embeddings (between -1 and 1)
        """
        # Normalize the embeddings (if they aren't already)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        embedding1_normalized = embedding1 / norm1
        embedding2_normalized = embedding2 / norm2
        
        # Calculate cosine similarity
        return float(np.dot(embedding1_normalized, embedding2_normalized))
    
    def search_similar(self, query_text: str, corpus: List[str], top_k: int = 5) -> List[dict]:
        """
        Search for texts similar to the query text within a corpus.
        
        Args:
            query_text: Text to search for
            corpus: List of texts to search within
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with text and similarity score
        """
        # Generate query embedding
        query_embedding = self.embed_text(query_text)
        
        # Generate embeddings for all texts in corpus
        corpus_embeddings = self.embed_text(corpus)
        
        # Calculate similarities
        similarities = []
        for i, embedding in enumerate(corpus_embeddings):
            sim = self.similarity(query_embedding, embedding)
            similarities.append((i, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for i, sim in similarities[:top_k]:
            results.append({
                "text": corpus[i],
                "similarity": sim
            })
        
        return results
    
    def embed_medical_concepts(self, concepts: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for medical concepts.
        
        Args:
            concepts: List of medical concept dictionaries
            
        Returns:
            Dictionary mapping concept IDs to embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
            
        # Initialize result dictionary
        embeddings = {}
        
        # Process each concept
        for concept in concepts:
            # Get concept ID and text
            concept_id = str(concept.get("id", ""))
            concept_text = concept.get("text", concept.get("name", ""))
            
            if not concept_id or not concept_text:
                logger.warning(f"Skipping concept with missing ID or text: {concept}")
                continue
            
            # Generate embedding
            try:
                embedding = self.embed_text(concept_text)
                embeddings[concept_id] = embedding
            except Exception as e:
                logger.error(f"Error generating embedding for concept {concept_id}: {e}")
        
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return float(similarity)
    
    def find_most_similar(self, 
                         query_embedding: np.ndarray, 
                         target_embeddings: List[np.ndarray], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find the most similar embeddings to a query embedding.
        
        Args:
            query_embedding: Embedding to compare against
            target_embeddings: List of embeddings to search
            top_k: Number of top matches to return
            
        Returns:
            List of dictionaries with indices and similarity scores
        """
        if not target_embeddings:
            return []
            
        # Compute similarities
        similarities = [
            (i, self.compute_similarity(query_embedding, target_embedding))
            for i, target_embedding in enumerate(target_embeddings)
        ]
        
        # Sort by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k matches
        return [
            {"index": idx, "score": score}
            for idx, score in similarities[:top_k]
        ]
        
    def embed_documents(self, 
                       documents: List[Dict[str, Any]], 
                       chunk_size: int = 512,
                       chunk_overlap: int = 50,
                       normalize: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate embeddings for document chunks.
        
        This method splits documents into overlapping chunks for more effective retrieval.
        
        Args:
            documents: List of document dictionaries with 'id' and 'text' keys
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters overlap between chunks
            normalize: Whether to normalize embeddings
            
        Returns:
            Dictionary mapping document IDs to lists of chunk embeddings with metadata
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
            
        result = {}
        
        for doc in documents:
            doc_id = doc.get('id', str(hash(doc.get('text', ''))))
            text = doc.get('text', '')
            
            # Skip empty documents
            if not text:
                continue
                
            # Create chunks
            chunks = []
            start = 0
            
            while start < len(text):
                # Calculate end position with respect to chunk size
                end = min(start + chunk_size, len(text))
                
                # If not at the end of the text, try to find a good break point
                if end < len(text):
                    # Try to break at a sentence boundary
                    sentence_break = text.rfind('.', start, end)
                    if sentence_break > start + chunk_size // 2:  # If we can find a good sentence break
                        end = sentence_break + 1  # Include the period
                    else:
                        # Try to break at a word boundary
                        word_break = text.rfind(' ', start, end)
                        if word_break > start + chunk_size // 2:  # If we can find a good word break
                            end = word_break
                
                # Add the chunk
                chunk_text = text[start:end].strip()
                if chunk_text:  # Skip empty chunks
                    chunks.append({
                        'text': chunk_text,
                        'start': start,
                        'end': end
                    })
                
                # Move start position for next chunk, with overlap
                start = max(start + 1, end - chunk_overlap)
            
            # Generate embeddings for all chunks in this document
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_embeddings = self.model.encode(
                chunk_texts, 
                normalize_embeddings=normalize,
                show_progress_bar=len(chunk_texts) > 10
            )
            
            # Combine chunk metadata with embeddings
            result[doc_id] = []
            for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                result[doc_id].append({
                    'chunk_id': f"{doc_id}_{i}",
                    'text': chunk['text'],
                    'start': chunk['start'],
                    'end': chunk['end'],
                    'embedding': embedding
                })
        
        return result

    def create_specialized_medical_embedding(self, text: str, context_terms: List[str], normalize: bool = True) -> np.ndarray:
        """
        Create a specialized medical embedding with domain-specific context.
        
        This method enhances the embedding by combining the text with relevant
        medical context terms to improve domain-specific matching.
        
        Args:
            text: Primary text to embed
            context_terms: Medical context terms to include for domain enrichment
            normalize: Whether to normalize the embedding
            
        Returns:
            Enhanced embedding vector
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
            
        # Create a version with medical context terms added
        enhanced_text = text
        
        # Add relevant context terms if they're not already in the text
        for term in context_terms:
            if term.lower() not in text.lower():
                enhanced_text += f" {term}"
        
        # Create both standard and enhanced embeddings
        standard_embedding = self.model.encode(text, normalize_embeddings=normalize)
        enhanced_embedding = self.model.encode(enhanced_text, normalize_embeddings=normalize)
        
        # Blend the embeddings (70% standard, 30% enhanced)
        # This keeps the original meaning while adding medical context
        blended_embedding = 0.7 * standard_embedding + 0.3 * enhanced_embedding
        
        # Normalize if requested
        if normalize:
            blended_embedding = blended_embedding / np.linalg.norm(blended_embedding)
            
        return blended_embedding 