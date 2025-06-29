"""
Medical RAG (Retrieval Augmented Generation) Module.

Provides tools for building and querying a medical knowledge base
using retrieval augmented generation techniques.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
import os
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from transformers import logging as hf_logging

# Reduce verbosity of transformers warnings
hf_logging.set_verbosity_error()

class MedicalRAG:
    """
    Retrieval Augmented Generation for medical data, optimized for
    retrieving relevant medical context for questions and generation.
    """
    
    def __init__(
        self,
        embedding_model_name: Optional[str] = None,
        llm_model_name: Optional[str] = None,
        use_gpu: bool = True,
        vector_store_path: Optional[str] = None
    ):
        """
        Initialize the medical RAG system.
        
        Args:
            embedding_model_name: Name of the embedding model to use
            llm_model_name: Name of the language model to use
            use_gpu: Whether to use GPU acceleration if available
            vector_store_path: Path to save/load the vector store
        """
        self.embedding_model_name = embedding_model_name or "pritamdeka/S-PubMedBert-MS-MARCO"
        self.llm_model_name = llm_model_name or "google/flan-t5-base"
        self.use_gpu = use_gpu
        self.vector_store_path = vector_store_path
        
        # Initialize components
        self._initialize_models()
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None
    
    def _initialize_models(self):
        """Initialize the embedding and language models."""
        try:
            # Set up the embedding model
            print(f"Loading embedding model: {self.embedding_model_name}")
            model_kwargs = {'device': 'cuda' if self.use_gpu else 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
            # Set up the LLM
            print(f"Loading language model: {self.llm_model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_name)
            
            # Handle device placement more carefully to avoid platform-specific issues
            if self.use_gpu:
                try:
                    # Try using device_map="auto" first
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.llm_model_name,
                        device_map="auto",
                        load_in_8bit=True
                    )
                except Exception as e:
                    print(f"Warning: Couldn't use automatic device mapping: {e}")
                    # Fall back to explicit device assignment
                    import torch
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.llm_model_name,
                        device_map=None,
                        load_in_8bit=False
                    )
                    self.model = self.model.to(device)
            else:
                # CPU-only loading without quantization
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.llm_model_name,
                    device_map=None,
                    load_in_8bit=False
                )
            
            # Create a text generation pipeline
            self.text_pipeline = pipeline(
                "text2text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=512,
                temperature=0.3,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            # Create LangChain LLM wrapper
            self.llm = HuggingFacePipeline(pipeline=self.text_pipeline)
            
            # Initialize text splitter for document chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            self.models_loaded = True
            print("Models loaded successfully")
        except Exception as e:
            print(f"Error initializing models: {e}")
            self.models_loaded = False
    
    def add_documents(self, documents: List[Dict[str, Any]], create_new: bool = False) -> bool:
        """
        Add documents to the medical knowledge base.
        
        Args:
            documents: List of document dictionaries with 'text' and other metadata
            create_new: Whether to create a new vector store or add to existing
            
        Returns:
            Success status
        """
        if not self.models_loaded:
            print("Models not loaded, cannot add documents")
            return False
            
        try:
            # Convert to LangChain document format
            langchain_docs = []
            
            for doc in documents:
                text = doc.get('text', '')
                metadata = {k: v for k, v in doc.items() if k != 'text'}
                
                langchain_docs.append(Document(
                    page_content=text,
                    metadata=metadata
                ))
            
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(langchain_docs)
            print(f"Splitting {len(langchain_docs)} documents into {len(split_docs)} chunks")
            
            # Create or update vector store
            if create_new or self.vector_store is None:
                print("Creating new vector store")
                self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
                
                # Save if path is specified
                if self.vector_store_path:
                    self.vector_store.save_local(self.vector_store_path)
            else:
                print("Adding to existing vector store")
                self.vector_store.add_documents(split_docs)
                
                # Save if path is specified
                if self.vector_store_path:
                    self.vector_store.save_local(self.vector_store_path)
            
            # Create basic retriever
            self._initialize_retriever()
            
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def load_vector_store(self, path: Optional[str] = None) -> bool:
        """
        Load a vector store from disk.
        
        Args:
            path: Path to the vector store, defaults to self.vector_store_path
            
        Returns:
            Success status
        """
        if not self.models_loaded:
            print("Models not loaded, cannot load vector store")
            return False
            
        try:
            store_path = path or self.vector_store_path
            if not store_path:
                print("No vector store path specified")
                return False
                
            print(f"Loading vector store from {store_path}")
            self.vector_store = FAISS.load_local(store_path, self.embeddings)
            
            # Create basic retriever
            self._initialize_retriever()
            
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def _initialize_retriever(self):
        """Initialize the retriever with the current vector store."""
        if self.vector_store is None:
            print("No vector store available, cannot initialize retriever")
            return
            
        # Create basic retriever
        basic_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Create a filter to rerank and compress retrieved documents
        embeddings_filter = EmbeddingsFilter(
            embeddings=self.embeddings,
            similarity_threshold=0.7
        )
        
        # Create contextual compression retriever
        self.retriever = ContextualCompressionRetriever(
            base_compressor=embeddings_filter,
            base_retriever=basic_retriever
        )
        
        # Initialize QA chain
        self._initialize_qa_chain()
    
    def _initialize_qa_chain(self):
        """Initialize the question-answering chain."""
        if self.retriever is None or self.llm is None:
            print("Retriever or LLM not initialized, cannot create QA chain")
            return
            
        # Create a prompt template that emphasizes medical context
        template = """
        You are a helpful medical assistant with access to a patient's medical records.
        
        Relevant medical context from the patient records:
        {context}
        
        Based only on the context provided above, please answer the following question 
        about the patient's medical history. Be specific and concise.
        
        If the answer is not found in the provided context, just say "I don't have information 
        about that in your medical records" - never make up information.
        
        Question: {question}
        
        Answer:
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create the chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Simple context concatenation
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a medical question using the RAG system.
        
        Args:
            question: The medical question to answer
            
        Returns:
            Dictionary with answer and source documents
        """
        if not self.models_loaded or self.qa_chain is None:
            return {
                "answer": "I'm sorry, the medical knowledge system is not fully initialized.",
                "sources": []
            }
            
        try:
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            # Extract answer and sources
            answer = result.get("result", "No answer found")
            
            # Format source information
            sources = []
            source_docs = result.get("source_documents", [])
            
            for doc in source_docs:
                source = {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source)
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            print(f"Error answering question: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": []
            }
    
    def find_similar_medical_records(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Find medical records similar to the query text.
        
        Args:
            query_text: The text to find similar records for
            k: Number of similar records to return
            
        Returns:
            List of similar records with metadata and similarity scores
        """
        if not self.models_loaded or self.vector_store is None:
            return []
            
        try:
            # Get similar documents
            docs_and_scores = self.vector_store.similarity_search_with_score(query_text, k=k)
            
            # Format results
            results = []
            for doc, score in docs_and_scores:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                }
                results.append(result)
            
            return results
        except Exception as e:
            print(f"Error finding similar records: {e}")
            return []
    
    def get_medical_context(self, query: str, max_tokens: int = 2000) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Retrieve and format relevant medical context for a query.
        
        Args:
            query: The medical query to get context for
            max_tokens: Maximum number of tokens to include in the context
            
        Returns:
            Tuple of (formatted_context, source_documents)
        """
        if not self.models_loaded or self.retriever is None:
            return "", []
            
        try:
            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(query)
            
            # Track token count (rough estimate)
            total_tokens = 0
            selected_docs = []
            
            for doc in docs:
                # Estimate tokens as words/0.75 (rough approximation)
                doc_tokens = len(doc.page_content.split()) / 0.75
                
                if total_tokens + doc_tokens <= max_tokens:
                    selected_docs.append(doc)
                    total_tokens += doc_tokens
                else:
                    # If we can't fit the whole document, break
                    break
            
            # Format the context
            formatted_context = ""
            sources = []
            
            for i, doc in enumerate(selected_docs):
                # Add to formatted context
                formatted_context += f"Document {i+1}:\n{doc.page_content}\n\n"
                
                # Add to sources
                source = {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source)
            
            return formatted_context, sources
        except Exception as e:
            print(f"Error getting medical context: {e}")
            return "", []
    
    def create_medical_summary(self, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a medical summary based on patient information.
        
        Args:
            patient_info: Dictionary containing patient medical information
            
        Returns:
            Dictionary with generated summary and source information
        """
        if not self.models_loaded or self.qa_chain is None:
            return {
                "summary": "Cannot generate summary, system not fully initialized.",
                "sources": []
            }
            
        try:
            # Extract patient demographics and medical conditions
            name = patient_info.get("name", "the patient")
            age = patient_info.get("age", "")
            conditions = patient_info.get("conditions", [])
            
            # Create query to find relevant medical context
            conditions_text = ", ".join(conditions) if conditions else "medical history"
            query = f"{name} {age} with {conditions_text}"
            
            # Get relevant context
            context, sources = self.get_medical_context(query)
            
            # Create prompt for summary generation
            prompt = f"""
            Create a concise medical summary for {name}, age {age}, 
            who has the following conditions: {conditions_text}.
            
            Base your summary only on the following medical records:
            
            {context}
            
            Focus on the main medical conditions, key symptoms, treatments,
            and important events in chronological order. Do not include any
            information not supported by the medical records.
            
            Medical Summary:
            """
            
            # Generate summary
            outputs = self.text_pipeline(
                prompt,
                max_length=1024,
                temperature=0.3,
                top_p=0.95,
                repetition_penalty=1.15,
                do_sample=True
            )
            
            # Extract generated text
            summary = outputs[0]["generated_text"]
            
            # Remove the prompt from the response
            if summary.startswith(prompt):
                summary = summary[len(prompt):].strip()
            
            return {
                "summary": summary,
                "sources": sources
            }
        except Exception as e:
            print(f"Error creating medical summary: {e}")
            return {
                "summary": f"Error generating summary: {str(e)}",
                "sources": []
            }
    
    def get_condition_information(
        self, 
        condition: str,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve information about a specific medical condition.
        
        Args:
            condition: The name of the medical condition
            patient_context: Optional patient context to personalize the information
            
        Returns:
            Dictionary with condition information and sources
        """
        if not self.models_loaded or self.qa_chain is None:
            return {
                "information": "Cannot retrieve condition information, system not fully initialized.",
                "sources": []
            }
            
        try:
            # Create query to find relevant medical context
            query = f"{condition} medical condition"
            
            if patient_context:
                # Add patient-specific context to personalize the query
                conditions = patient_context.get("conditions", [])
                symptoms = patient_context.get("symptoms", [])
                
                if conditions:
                    query += f" related to {', '.join(conditions)}"
                if symptoms:
                    query += f" with symptoms including {', '.join(symptoms)}"
            
            # Get relevant context
            context, sources = self.get_medical_context(query)
            
            # Create prompt for condition information
            prompt = f"""
            Provide comprehensive information about {condition} based only on
            the following medical context:
            
            {context}
            
            Structure the information into the following sections:
            1. Description
            2. Symptoms
            3. Related conditions
            4. Management approaches
            
            Include only information supported by the provided context.
            """
            
            # Generate information
            outputs = self.text_pipeline(
                prompt,
                max_length=1024,
                temperature=0.3,
                top_p=0.95,
                repetition_penalty=1.15,
                do_sample=True
            )
            
            # Extract generated text
            information = outputs[0]["generated_text"]
            
            # Remove the prompt from the response
            if information.startswith(prompt):
                information = information[len(prompt):].strip()
            
            return {
                "information": information,
                "sources": sources
            }
        except Exception as e:
            print(f"Error retrieving condition information: {e}")
            return {
                "information": f"Error retrieving information: {str(e)}",
                "sources": []
            } 