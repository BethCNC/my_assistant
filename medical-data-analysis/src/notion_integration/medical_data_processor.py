"""
Medical Data Processor

This module provides the main class for processing medical documents,
extracting medical entities, and syncing data with Notion databases.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime
from pathlib import Path
import uuid

from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

from entity_extractor import EntityExtractor
from document_processor import DocumentProcessor
from notion_client import NotionClient
from notion_mapper import NotionEntityMapper

# Configure logging
logger = logging.getLogger(__name__)


class MedicalDataProcessor:
    """
    Main processor for medical data.
    
    Extracts entities from medical documents and syncs them to Notion databases.
    """
    
    def __init__(self, config=None):
        """
        Initialize the medical data processor with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        notion_api_key = self.config.get("notion_api_key")
        if not notion_api_key:
            raise ValueError("Notion API key is required")
            
        self.notion_client = NotionClient(api_key=notion_api_key)
        self.entity_extractor = EntityExtractor(self.config.get("entity_extraction"))
        self.notion_mapper = NotionEntityMapper(self.config.get("notion_mapping"))
        self.document_processor = DocumentProcessor()
        
        # Databases
        self._initialize_database_ids()
        
        self.logger.info("Medical data processor initialized")
        
    def _initialize_database_ids(self):
        """Initialize database IDs from config."""
        self.database_ids = {}
        db_config = self.config.get("notion_databases", {})
        
        for entity_type, db_id in db_config.items():
            if db_id:
                self.database_ids[entity_type] = db_id
                self.logger.debug(f"Using database ID for {entity_type}: {db_id}")

    def process_document(self, document_path, include_content=True):
        """
        Process a medical document and sync extracted data to Notion.
        
        Args:
            document_path: Path to the medical document
            include_content: Whether to include document content in Notion entries
            
        Returns:
            Dictionary of processed entities by type
        """
        self.logger.info(f"Processing document: {document_path}")
        
        try:
            # Extract document content and metadata
            document_summary = self.document_processor.get_document_summary(document_path)
            
            # Extract medical entities from the text
            entities = self.entity_extractor.extract_entities(
                text=document_summary["full_text"]
            )
            
            # Ensure entities is a dictionary
            if entities is None:
                entities = {}
            elif isinstance(entities, list):
                entities = {"entities": entities}
            
            # Add document itself to the entities
            document_entity = {
                "title": os.path.basename(document_path),
                "path": document_path,
                "document_date": document_summary["metadata"].get("document_date"),
                "created_time": document_summary["metadata"].get("created_time"),
                "modified_time": document_summary["metadata"].get("modified_time"),
                "extension": document_summary["metadata"].get("extension"),
                "metadata": document_summary["metadata"],
                "preview": document_summary["preview"],
                "word_count": document_summary["word_count"],
                "character_count": document_summary["character_count"],
                "full_text": document_summary["full_text"]
            }
            
            # Initialize "documents" key if it doesn't exist
            if "documents" not in entities:
                entities["documents"] = []
            entities["documents"].append(document_entity)
            
            # Sync all entities to Notion
            results = self.sync_entities_to_notion(entities, include_content)
            
            self.logger.info(f"Document processed successfully: {document_path}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing document {document_path}: {e}")
            raise

    def sync_entities_to_notion(self, entities, include_content=True):
        """
        Sync extracted entities to their respective Notion databases.
        
        Args:
            entities: Dictionary of entities by type
            include_content: Whether to include document content in Notion
            
        Returns:
            Dictionary of created/updated entities with their Notion IDs
        """
        results = {}
        entity_pages = {}
        
        # Process in a specific order to maintain relationships
        # (e.g., doctors before appointments)
        processing_order = [
            "documents", "doctors", "conditions", "medications", 
            "symptoms", "lab_results", "procedures", "appointments"
        ]
        
        for entity_type in processing_order:
            if entity_type not in entities or not entities[entity_type]:
                continue
                
            if entity_type not in self.database_ids:
                self.logger.warning(f"No database ID configured for {entity_type}, skipping")
                continue
                
            database_id = self.database_ids[entity_type]
            entities_of_type = entities[entity_type]
            
            self.logger.info(f"Syncing {len(entities_of_type)} {entity_type} to Notion")
            results[entity_type] = []
            
            for entity in entities_of_type:
                # Map entity to Notion properties
                properties = self.notion_mapper.map_entity_to_notion_properties(entity, entity_type)
                
                # Update properties with relationship references if needed
                properties = self._add_relationship_references(properties, entity, entity_type, entity_pages)
                
                # Create or update page in Notion
                page_id = self._create_or_update_notion_page(database_id, properties, entity, entity_type)
                
                if page_id:
                    # Add document content if requested and this is a document entity
                    if include_content and entity_type == "documents" and "full_text" in entity:
                        content_blocks = self._create_content_blocks_from_text(entity["full_text"])
                        
                        if content_blocks:
                            try:
                                # Add content blocks to the page
                                self.notion_client.append_blocks_to_page(page_id, content_blocks)
                                self.logger.debug(f"Added content blocks to document page {page_id}")
                            except Exception as e:
                                self.logger.error(f"Error adding content blocks to page {page_id}: {e}")
                    
                    # Keep track of entity page IDs for relationships
                    if entity_type not in entity_pages:
                        entity_pages[entity_type] = {}
                    
                    # Use a unique identifier for the entity based on name or ID
                    entity_key = entity.get("id") or entity.get("name") or str(uuid.uuid4())
                    entity_pages[entity_type][entity_key] = page_id
                    
                    # Store result
                    result = {
                        "entity": entity,
                        "notion_id": page_id,
                        "notion_url": f"https://notion.so/{page_id.replace('-', '')}"
                    }
                    results[entity_type].append(result)
        
        return results

    def _add_relationship_references(self, properties, entity, entity_type, entity_pages):
        """
        Add relationship references to entity properties.
        
        Args:
            properties: Dictionary of entity properties
            entity: Entity dictionary
            entity_type: Type of entity
            entity_pages: Dictionary of entity pages
            
        Returns:
            Updated properties dictionary
        """
        for key, value in entity.items():
            if key.endswith("_id") and isinstance(value, str) and value:
                relation_entity_type = key.replace("_id", "")
                if relation_entity_type not in entity_pages:
                    entity_pages[relation_entity_type] = {}
                # Create a relation property if needed
                if key in properties:
                    # We have a properly formatted relation already
                    pass
                else:
                    # Add as plain text for now - the mapper should handle conversion
                    properties[key] = value
        
        return properties

    def _create_or_update_notion_page(self, database_id, properties, entity, entity_type):
        """
        Create or update a Notion page for an entity.
        
        Args:
            database_id: ID of the Notion database
            properties: Dictionary of entity properties
            entity: Entity dictionary
            entity_type: Type of entity
            
        Returns:
            ID of the created or updated page
        """
        try:
            page_id = self.notion_client.find_or_create_page(
                database_id=database_id,
                properties=properties
            )
            
            if page_id:
                self.logger.debug(f"Created or updated page {page_id} for {entity_type}")
            else:
                self.logger.warning(f"Failed to create or update page for {entity_type}")
            
            return page_id
        except Exception as e:
            self.logger.error(f"Error creating/updating page for {entity_type}: {e}")
            return None

    def _create_content_blocks_from_text(self, text):
        """
        Create Notion content blocks from text.
        
        Args:
            text: Document text
            
        Returns:
            List of Notion content blocks
        """
        if not text:
            return []
            
        # Split text into paragraphs
        paragraphs = text.split("\n\n")
        
        # Create blocks
        blocks = []
        
        # Add a heading for document content
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Document Content"
                        }
                    }
                ]
            }
        })
        
        # Add paragraphs
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": paragraph.strip()
                            }
                        }
                    ]
                }
            })
            
        return blocks

    def process_directory(self, directory_path: Union[str, Path],
                         recursive: bool = False,
                         file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process all medical documents in a directory
        
        Args:
            directory_path: Path to directory containing documents
            recursive: Whether to process subdirectories
            file_extensions: List of file extensions to process (e.g. ['.pdf', '.txt'])
            
        Returns:
            Dictionary mapping file paths to processing results
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Directory not found: {directory_path}")
            
        file_extensions = file_extensions or ['.pdf', '.txt', '.docx', '.html', '.md']
        
        # Get list of files
        files = []
        if recursive:
            for ext in file_extensions:
                files.extend(directory_path.glob(f"**/*{ext}"))
        else:
            for ext in file_extensions:
                files.extend(directory_path.glob(f"*{ext}"))
                
        logger.info(f"Found {len(files)} files to process in {directory_path}")
        
        # Process each file
        results = {}
        for file_path in files:
            try:
                results[str(file_path)] = self.process_document(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results[str(file_path)] = {"error": str(e)}
                
        return results


def process_document_file(file_path: str) -> Union[Dict[str, Any], None]:
    """Process a single document file and return extracted entities.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Dictionary of extracted entities or None if extraction fails
    """
    # Create processor with default config
    processor = MedicalDataProcessor()
    
    # Process the document
    return processor.process_document(file_path) 