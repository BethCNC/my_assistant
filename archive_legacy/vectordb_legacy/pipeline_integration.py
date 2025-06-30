"""
Vector Database Pipeline Integration Module

This module connects the medical vector store with the ingestion pipeline,
enabling semantic search and retrieval of processed medical data.
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.ai.vectordb.medical_vector_store import MedicalVectorStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle numpy arrays
class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy arrays by converting them to lists."""
    
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)

class VectorDBPostProcessor:
    """
    Post-processor for the ingestion pipeline that adds documents and entities to the vector database.
    """
    
    def __init__(
        self,
        vector_db_path: str = "vectordb",
        embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO",
        use_gpu: bool = False
    ):
        """
        Initialize the vector database post-processor.
        
        Args:
            vector_db_path: Path to store vector database files
            embedding_model: Name of the embedding model to use
            use_gpu: Whether to use GPU for embedding generation
        """
        self.vector_integration = VectorDBIntegration(
            vector_db_path=vector_db_path,
            embedding_model=embedding_model,
            use_gpu=use_gpu
        )
        logger.info(f"Initialized Vector DB Post Processor with model {embedding_model}")
    
    def process(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and add it to the vector database.
        Implements the post-processor interface required by the ingestion pipeline.
        
        Args:
            document_data: Document data from the pipeline
            
        Returns:
            Updated document data with vector IDs
        """
        return self.vector_integration.process_extracted_document(document_data)

class VectorDBIntegration:
    """
    Integration between the ingestion pipeline and vector database,
    enabling semantic search and similarity analysis across medical data.
    """
    
    def __init__(
        self,
        vector_db_path: str = "vectordb",
        embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO",
        use_gpu: bool = False,
        vector_store: MedicalVectorStore = None
    ):
        """
        Initialize the vector database integration.
        
        Args:
            vector_db_path: Path to store vector database files
            embedding_model: Name of the embedding model to use
            use_gpu: Whether to use GPU for embedding generation
            vector_store: Optional pre-initialized vector store to use
        """
        self.vector_db_path = Path(vector_db_path)
        self.embedding_model = embedding_model
        self.use_gpu = use_gpu
        
        # Use provided vector store or initialize a new one
        if vector_store:
            self.vector_store = vector_store
        else:
            # Initialize vector store
            self.vector_store = MedicalVectorStore(
                storage_path=vector_db_path,
                embedding_model=embedding_model,
                use_gpu=use_gpu
            )
        
        logger.info(f"Initialized Vector DB Integration with model {embedding_model}")
    
    def process_extracted_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an extracted document and add it to the vector database.
        
        Args:
            document_data: Extracted document data from the pipeline
            
        Returns:
            Updated document data with vector IDs
        """
        try:
            # First convert any numpy arrays to Python native types
            document_data_copy = json.loads(json.dumps(document_data, cls=NumpyEncoder))
            
            # Extract document ID
            document_id = document_data_copy.get("id") or document_data_copy.get("metadata", {}).get("file_path")
            if not document_id:
                document_id = str(hash(json.dumps(document_data_copy, sort_keys=True)))
            
            # Extract document text
            if "content" in document_data_copy:
                document_text = document_data_copy["content"]
            elif "text" in document_data_copy:
                document_text = document_data_copy["text"]
            else:
                document_text = str(document_data_copy)
            
            # Extract metadata
            metadata = document_data_copy.get("metadata", {}).copy()
            
            # Add document type to metadata if available
            if "document_type" in document_data_copy:
                metadata["document_type"] = document_data_copy["document_type"]
            
            # Add document to vector store
            vector_id = self.vector_store.add_document(
                document_id=document_id,
                text=document_text,
                metadata=metadata
            )
            
            # Update document data with vector ID
            if "vector_db" not in document_data:
                document_data["vector_db"] = {}
            
            document_data["vector_db"]["document_vector_id"] = vector_id
            
            # Process entities if available
            if "ai_analysis" in document_data_copy and "entities" in document_data_copy["ai_analysis"]:
                self._process_entities(document_data, document_id)
            
            logger.info(f"Added document to vector store: {document_id}")
            
            return document_data
        except Exception as e:
            logger.error(f"Error processing document for vector database: {e}")
            if "vector_db" not in document_data:
                document_data["vector_db"] = {}
            document_data["vector_db"]["error"] = str(e)
            return document_data
    
    def _process_entities(self, document_data: Dict[str, Any], document_id: str) -> None:
        """
        Process entities from AI analysis and add them to the vector database.
        
        Args:
            document_data: Document data containing AI analysis
            document_id: ID of the parent document
        """
        # Use NumpyEncoder to handle any numpy arrays in the entities
        try:
            ai_analysis = json.loads(json.dumps(document_data["ai_analysis"], cls=NumpyEncoder))
            
            # Check if entities is a dictionary or list
            entities = ai_analysis.get("entities", {})
            if not entities:
                logger.warning("No entities found in AI analysis")
                return
                
            entity_vector_ids = {}
            
            # Handle different entity structures
            # Case 1: If entities is a dictionary with entity types as keys
            if isinstance(entities, dict):
                for entity_type, entity_list in entities.items():
                    if not isinstance(entity_list, list):
                        logger.warning(f"Expected list for entity type {entity_type}, got {type(entity_list)}")
                        continue
                        
                    for entity in entity_list:
                        self._add_entity_to_vector_db(entity, entity_type, document_id, entity_vector_ids)
            
            # Case 2: If entities is a list of entity objects with a 'type' field
            elif isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict) and "type" in entity:
                        entity_type = entity["type"]
                        self._add_entity_to_vector_db(entity, entity_type, document_id, entity_vector_ids)
                    else:
                        logger.warning(f"Entity missing 'type' field: {entity}")
            
            # Update document data with entity vector IDs
            if entity_vector_ids and "vector_db" in document_data:
                document_data["vector_db"]["entity_vector_ids"] = entity_vector_ids
                
        except Exception as e:
            logger.error(f"Error processing entities for vector database: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def _add_entity_to_vector_db(self, entity: Dict[str, Any], entity_type: str, document_id: str, entity_vector_ids: Dict[str, List[str]]) -> None:
        """
        Add a single entity to the vector database.
        
        Args:
            entity: The entity data
            entity_type: The type of entity
            document_id: The parent document ID
            entity_vector_ids: Dictionary to store the vector IDs
        """
        # Map entity types to vector DB categories
        entity_type_mapping = {
            "MEDICATION": "medications",
            "CONDITION": "conditions",
            "SYMPTOM": "symptoms",
            "PROCEDURE": "procedures",
            "LAB_RESULT": "lab_results",
            "TEST_RESULT": "lab_results"
        }
        
        # Get standardized entity type
        entity_category = entity_type_mapping.get(entity_type.upper(), "other")
        
        # Get entity name/text
        entity_text = entity.get("name", "")
        if not entity_text and "text" in entity:
            entity_text = entity["text"]
        if not entity_text:
            entity_text = str(entity)
            
        # Get entity metadata
        entity_metadata = {
            "entity_type": entity_type,
            "document_id": document_id
        }
        
        # Add relevant fields to metadata
        for field in ["code", "code_system", "value", "unit", "date", "status"]:
            if field in entity and entity[field]:
                entity_metadata[field] = entity[field]
                
        # Create entity ID
        entity_id = f"{document_id}_{entity_type}_{hash(entity_text)}"
        
        try:
            # Add entity to vector store
            vector_id = self.vector_store.add_entity(
                entity_id=entity_id,
                text=entity_text,
                entity_type=entity_category,
                metadata=entity_metadata
            )
            
            # Store vector ID
            if entity_category not in entity_vector_ids:
                entity_vector_ids[entity_category] = []
            entity_vector_ids[entity_category].append(vector_id)
            
        except Exception as e:
            logger.error(f"Error adding entity to vector DB: {str(e)}")
    
    def find_similar_documents(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to the query text.
        
        Args:
            query_text: Query text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        return self.vector_store.search(query_text, entity_types=["documents"], limit=limit)
    
    def find_similar_conditions(self, condition_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find conditions similar to the query text.
        
        Args:
            condition_text: Condition text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of similar conditions with similarity scores
        """
        return self.vector_store.get_similar_conditions(condition_text, limit=limit)
    
    def find_similar_symptoms(self, symptom_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find symptoms similar to the query text.
        
        Args:
            symptom_text: Symptom text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of similar symptoms with similarity scores
        """
        return self.vector_store.get_similar_symptoms(symptom_text, limit=limit)
    
    def find_documents_by_medical_concept(self, concept_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents related to a medical concept.
        
        Args:
            concept_text: Medical concept text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of related documents with similarity scores
        """
        return self.vector_store.find_related_documents(concept_text, limit=limit)
    
    def integrate_with_pipeline(self, pipeline_instance) -> None:
        """
        Integrate with a medical data pipeline instance.
        
        Args:
            pipeline_instance: Instance of MedicalDataIngestionPipeline
        """
        # Check if pipeline has the register_post_processor method
        if hasattr(pipeline_instance, "register_post_processor"):
            # Register vector DB integration as a post-processor
            pipeline_instance.register_post_processor(self.process_extracted_document)
            logger.info("Registered vector DB integration with pipeline")
        else:
            logger.warning("Pipeline does not support post-processors, integration must be done manually")

    def process(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and add it to the vector database.
        This is an alias for process_extracted_document to match test expectations.
        
        Args:
            document_data: Document data from the pipeline
            
        Returns:
            Updated document data with vector IDs
        """
        return self.process_extracted_document(document_data)


# Utility function to create and integrate vector database with a pipeline
def create_vector_db_integration(
    pipeline=None,
    vector_db_path: str = "vectordb",
    embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO", 
    use_gpu: bool = False
) -> VectorDBIntegration:
    """
    Create a vector database integration and optionally integrate with a pipeline.
    
    Args:
        pipeline: Optional pipeline instance to integrate with
        vector_db_path: Path to store vector database files
        embedding_model: Name of the embedding model to use
        use_gpu: Whether to use GPU for embedding generation
        
    Returns:
        Configured VectorDBIntegration instance
    """
    integration = VectorDBIntegration(
        vector_db_path=vector_db_path,
        embedding_model=embedding_model,
        use_gpu=use_gpu
    )
    
    if pipeline is not None:
        integration.integrate_with_pipeline(pipeline)
    
    return integration 