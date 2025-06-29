#!/usr/bin/env python
"""
End-to-end data ingestion pipeline for medical data processing.

This module coordinates the extraction, processing, AI analysis, and database storage
of medical documents from various formats into the structured database.
"""

import os
import sys
import logging
import json
import numpy as np
import shutil
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Type, cast
import glob

# Database imports
from sqlalchemy.orm import Session
from src.database.session import get_session, DatabaseSession

# Custom modules
from src.extraction.factory import get_extractor
from src.extraction.base import BaseExtractor
from src.processing.factory import process_document, get_processor, determine_document_type
from src.ai.entity_extraction import MedicalEntityExtractor
from src.ai.text_analysis import MedicalTextAnalyzer
from src.ai.embedding import MedicalEmbedding
from src.ai.model_integration import ModelIntegration
from src.database.dao import (
    DocumentDAO, PatientDAO, ProviderDAO,
    ConditionDAO, MedicationDAO, SymptomDAO,
    MedicalEventDAO, LabResultDAO
)
from src.database.models.entity import (
    Document, Patient, HealthcareProvider, Condition, 
    Medication, Symptom, MedicalEvent, LabResult
)
from src.ai.vectordb.pipeline_integration import VectorDBPostProcessor, VectorDBIntegration
from src.ai.entity_standardization import standardize_entities
from src.extraction.utils import is_supported_file_type


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Pipeline for ingesting and processing medical documents.
    
    Handles document extraction, processing, AI analysis, and storage.
    """
    
    def __init__(
        self,
        input_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        processed_dir: Optional[Union[str, Path]] = None,
        models_dir: Optional[Union[str, Path]] = None,
        session: Optional[Union[Session, DatabaseSession]] = None,
        use_gpu: bool = False
    ):
        """
        Initialize the ingestion pipeline.
        
        Args:
            input_dir: Directory containing files to process
            output_dir: Directory to store output files
            processed_dir: Directory to store processed results
            models_dir: Directory containing AI models, if any
            session: Database session
            use_gpu: Whether to use GPU for AI processing
        """
        # Initialize directories
        self.input_dir = Path(input_dir) if input_dir else Path("data/input")
        self.output_dir = Path(output_dir) if output_dir else Path("data/output")
        self.processed_dir = Path(processed_dir) if processed_dir else Path("data/processed")
        self.models_dir = Path(models_dir) if models_dir else Path("models")
        
        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session
        self.session = session if session else get_session()
        self.use_gpu = use_gpu
        
        # Initialize DAOs
        self.document_dao = DocumentDAO(self.session)
        self.patient_dao = PatientDAO(self.session)
        self.provider_dao = ProviderDAO(self.session)
        self.condition_dao = ConditionDAO(self.session)
        self.medication_dao = MedicationDAO(self.session)
        self.symptom_dao = SymptomDAO(self.session)
        self.event_dao = MedicalEventDAO(self.session)
        self.lab_result_dao = LabResultDAO(self.session)
        
        # Initialize AI components
        self.entity_extractor = None
        self.text_analyzer = None
        self.model_integration = None
        
        # Set up post-processors
        self.post_processors: List[Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]] = []
        
        # Import and initialize AI modules
        self._import_modules()
    
    def _import_modules(self) -> None:
        """Import necessary AI modules and initialize them."""
        try:
            # Create entity extractor
            self.entity_extractor = MedicalEntityExtractor()
            
            # Create text analyzer
            self.text_analyzer = MedicalTextAnalyzer()
            
            # Create model integration
            self.model_integration = ModelIntegration(
                use_entity_extraction=True,
                use_text_analysis=True,
                use_embedding=True
            )
            
            logger.info("AI modules imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import AI modules: {str(e)}")
            self.entity_extractor = None
            self.text_analyzer = None
            self.model_integration = None
        except Exception as e:
            logger.warning(f"Error initializing AI modules: {str(e)}")
            self.entity_extractor = None
            self.text_analyzer = None
            self.model_integration = None
    
    def register_post_processor(self, processor: Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]) -> None:
        """
        Register a post-processor function to be called on each processed document.
        
        Args:
            processor: Function that takes a processed document dictionary and performs additional processing.
                      May return an updated document or None.
        """
        self.post_processors.append(processor)
    
    def process_directory(self, directory: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        Process all files in a directory.
        
        Args:
            directory: Directory containing files to process (defaults to input_dir)
            
        Returns:
            List of dictionaries with processing results
        """
        directory = Path(directory) if directory else self.input_dir
        results = []
        
        logger.info(f"Processing directory: {directory}")
        
        # Check if directory exists
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return []
        
        # Get all files in directory
        files = [f for f in directory.glob("**/*") if f.is_file()]
        logger.info(f"Found {len(files)} files")
        
        # Process each file
        for file_path in files:
            result = self.process_file(file_path)
            if result:
                results.append(result)
        
        return results
    
    def _get_extractor_for_file(self, file_path: Path) -> Optional[BaseExtractor]:
        """
        Get the appropriate extractor for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            An extractor instance or None if no suitable extractor is found
        """
        extractor = get_extractor(file_path)
        if not extractor:
            logger.warning(f"No suitable extractor found for {file_path}")
        return extractor
        
    def process_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a single file through the pipeline.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary with processing results
        """
        file_path = Path(file_path)
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Check if file exists and is a file
            if not file_path.exists():
                return {"error": f"File not found: {file_path}"}
            if not file_path.is_file():
                return {"error": f"Not a file: {file_path}"}
                
            # Check if the file is of a supported type
            if not self._is_supported_file_type(file_path):
                return {"error": f"Unsupported file type: {file_path}"}
            
            # Extract text from file
            processed_data = self._process_file(file_path)
            if processed_data is None:
                return {"error": f"Failed to extract text from file: {file_path}"}
            
            # Analyze text with AI models
            ai_result = self._analyze_document(
                processed_data.get("content", ""),
                processed_data.get("metadata", {})
            )
            processed_data["ai_analysis"] = ai_result
            
            # Store in database
            self._store_in_database(processed_data)
            
            # Create a serializable copy without non-serializable objects
            serializable_data = self._create_serializable_copy(processed_data)
            
            # Save processed results
            output_path = self._save_processed_file(
                file_path,
                processed_data.get("content", ""),
                processed_data.get("metadata", {}),
                ai_result
            )
            serializable_data["output_path"] = str(output_path)
            
            # Run post-processors
            for processor in self.post_processors:
                try:
                    result = processor(serializable_data)
                    if result:
                        serializable_data = result
                except Exception as e:
                    logger.error(f"Error in post-processor: {str(e)}")
            
            return serializable_data
            
        except Exception as e:
            logger.error(f"Error processing file: {file_path}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _create_serializable_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a serializable copy of the processed data.
        
        Args:
            data: Original processed data
            
        Returns:
            Serializable copy of the data
        """
        result = {}
        
        # Copy all serializable fields
        for key, value in data.items():
            # Skip Document objects
            if key == "document" and isinstance(value, Document):
                # Include only basic information about the document
                result[key] = {
                    "id": value.id,
                    "document_type": value.document_type,
                    "document_date": value.document_date.isoformat() if value.document_date else None
                }
            else:
                result[key] = value
        
        return result
    
    def _process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single file and extract its contents.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary with extracted contents or None if extraction failed
        """
        extractor = self._get_extractor_for_file(file_path)
        if not extractor:
            return None
            
        try:
            # Use process_file method from the BaseExtractor implementation
            extracted_data = extractor.process_file(file_path)
            
            # Convert types for serialization
            if "extraction_date" in extracted_data and isinstance(extracted_data["extraction_date"], datetime):
                extracted_data["extraction_date"] = extracted_data["extraction_date"].isoformat()
            
            return extracted_data
        except Exception as e:
            logger.error(f"Error extracting from file {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def _analyze_document(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze document text with AI models.
        
        Args:
            text: Text to analyze
            metadata: Document metadata
            
        Returns:
            Dictionary with analysis results
        """
        result = {"entities": [], "analysis": {}, "embeddings": {}}
        
        if self.model_integration is None:
            logger.warning("No model integration available for document analysis")
            return result
            
        try:
            # Extract entities from text
            entities = self.model_integration.extract_entities(text) or []
            result["entities"] = entities
            
            # Analyze text
            analysis = self.model_integration.analyze_text(text) or {}
            result["analysis"] = analysis
            
            # Generate embeddings if method exists
            if hasattr(self.model_integration, "generate_embedding"):
                embedding = self.model_integration.generate_embedding(text)
                if embedding is not None:
                    result["embeddings"]["document"] = embedding
            
            logger.info("Document analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            logger.error(traceback.format_exc())
            return result
    
    def _store_in_database(self, processed_data: Dict[str, Any]) -> bool:
        """
        Store processed document data in the database.
        
        Args:
            processed_data: Dictionary with processed document data
            
        Returns:
            True if storage succeeded, False otherwise
        """
        if not self.session:
            logger.warning("No database session available")
            return False
        
        try:
            # Create document record
            processed_data["document"] = Document(
                document_type=processed_data.get("metadata", {}).get("document_type", "unknown"),
                content=processed_data.get("content", ""),
                patient_id=1,  # Default to patient ID 1 for now, would be determined in production
                provider_id=processed_data.get("metadata", {}).get("provider_id"),
                document_date=processed_data.get("metadata", {}).get("document_date"),
                source=processed_data.get("metadata", {}).get("source", "unknown")
            )
            self.document_dao.create(processed_data["document"])
            
            logger.info(f"Document stored in database with ID: {processed_data['document'].id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing document in database: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _save_processed_file(self, file_path: Path, text: str, metadata: Dict[str, Any], ai_result: Dict[str, Any]) -> Path:
        """
        Save processed results to a file.
        
        Args:
            file_path: Original file path
            text: Extracted text
            metadata: Document metadata
            ai_result: AI analysis results
            
        Returns:
            Path to the saved file
        """
        try:
            # Create a sanitized filename
            result_filename = self.processed_dir / f"{file_path.stem}_processed.json"
            
            # Create serializable data
            serializable_data = {
                "original_file": str(file_path),
                "extraction_date": datetime.now().isoformat(),
                "content": text,
                "metadata": metadata,
                "ai_analysis": self._make_json_serializable(ai_result)
            }
            
            # Save to file
            with open(result_filename, 'w', encoding='utf-8') as f:
                try:
                    # Get the NumpyEncoder if available
                    from src.ai.vectordb.numpy_json import NumpyEncoder
                    json.dump(serializable_data, f, cls=NumpyEncoder, indent=2)
                except ImportError:
                    # Fall back to default encoder with custom handling
                    json.dump(serializable_data, f, default=self._json_serialize_handler, indent=2)
            
            logger.info(f"Saved processed results to {result_filename}")
            return result_filename
            
        except Exception as e:
            logger.error(f"Error saving processed file: {str(e)}")
            logger.error(traceback.format_exc())
            # Return a default path in case of error
            return self.processed_dir / f"error_{uuid.uuid4()}.json"
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """
        Convert an object to a JSON serializable format.
        
        Args:
            obj: Object to convert
            
        Returns:
            JSON serializable version of the object
        """
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (datetime, np.datetime64)):
            return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, (Document, Patient, HealthcareProvider, Condition, 
                             Medication, Symptom, MedicalEvent, LabResult)):
            # Convert ORM objects to dictionaries
            return {"id": getattr(obj, "id", str(uuid.uuid4())), "type": obj.__class__.__name__}
        else:
            return obj
    
    def _json_serialize_handler(self, obj: Any) -> Any:
        """
        JSON serialization handler for custom types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON serializable version of the object
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            # Handle ORM objects
            return {"id": getattr(obj, "id", str(uuid.uuid4())), "type": obj.__class__.__name__}
        else:
            return str(obj)
    
    def _is_supported_file_type(self, file_path: Path) -> bool:
        """
        Check if a file is of a supported type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is of a supported type, False otherwise
        """
        supported_extensions = [
            '.txt', '.csv', '.html', '.htm', '.pdf', 
            '.doc', '.docx', '.rtf', '.md', '.json'
        ]
        return file_path.suffix.lower() in supported_extensions
    
    def register_vector_db(self, vector_db_path: Union[str, Path] = "data/vector_db"):
        """
        Register vector database integration as a post-processor.
        
        Args:
            vector_db_path: Path to store vector database
        """
        try:
            from src.ai.vectordb.pipeline_integration import VectorDBPostProcessor
            
            # Create vector DB post-processor with correct parameter names
            vector_db = VectorDBPostProcessor(
                vector_db_path=str(vector_db_path),  # Convert Path to str
                embedding_model="pritamdeka/S-PubMedBert-MS-MARCO",
                use_gpu=self.use_gpu
            )
            
            # Register as post-processor
            self.register_post_processor(vector_db)
            logger.info(f"Vector database registered with path: {vector_db_path}")
            
        except ImportError as e:
            logger.warning(f"Could not import vector database integration: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error registering vector database: {str(e)}")
            
    def close(self):
        """
        Clean up resources used by the pipeline.
        """
        try:
            # Close database session if exists
            if hasattr(self, 'session') and self.session is not None:
                try:
                    logger.info("Closing database session")
                    self.session.close()
                except Exception as e:
                    logger.error(f"Error closing database session: {str(e)}")
            
            # Close vector database if exists
            for processor in self.post_processors:
                if hasattr(processor, 'close'):
                    try:
                        logger.info(f"Closing post-processor: {processor.__class__.__name__}")
                        processor.close()
                    except Exception as e:
                        logger.error(f"Error closing post-processor: {str(e)}")
            
            logger.info("Pipeline resources cleaned up")
        except Exception as e:
            logger.error(f"Error during pipeline cleanup: {str(e)}")


def main():
    """Command-line entry point for the ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Medical Data Ingestion Pipeline")
    parser.add_argument("input_path", help="Path to file or directory to process")
    parser.add_argument("--no-models", action="store_true", help="Disable AI models (use rule-based fallbacks)")
    parser.add_argument("--no-db", action="store_true", help="Don't store results in database")
    parser.add_argument("--output", "-o", default="processed_data", help="Directory to store processed results")
    parser.add_argument("--use-gpu", action="store_true", help="Use GPU for model inference if available")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = IngestionPipeline(
        use_gpu=args.use_gpu
    )
    
    try:
        # Process input path
        input_path = Path(args.input_path)
        
        if input_path.is_file():
            result = pipeline.process_file(input_path)
            if "error" in result:
                logger.error(f"Error processing file: {result['error']}")
                return 1
        elif input_path.is_dir():
            results = pipeline.process_directory(input_path)
            errors = [r for r in results if "error" in r]
            if errors:
                logger.error(f"Encountered {len(errors)} errors during processing")
                for error in errors:
                    logger.error(f"  - {error['file_path']}: {error['error']}")
                return 1
        else:
            logger.error(f"Input path does not exist: {input_path}")
            return 1
        
        logger.info("Processing completed successfully")
        return 0
    
    finally:
        # Clean up resources
        pipeline.close()


if __name__ == "__main__":
    sys.exit(main()) 