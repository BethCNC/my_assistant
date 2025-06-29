"""
Configuration settings for the medical data processing system.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", str(BASE_DIR / "processed_data"))

# Database configuration
DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{str(BASE_DIR / 'medical_data.db')}")

# AI model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
NER_MODEL = os.getenv("NER_MODEL", "en_core_web_lg")

# API configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Document storage settings
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")  # "local" or "minio"
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
DOCUMENT_BUCKET = os.getenv("DOCUMENT_BUCKET", "medical-documents")

# Create directories if they don't exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Vector database
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "")
VECTOR_DB_API_KEY = os.getenv("VECTOR_DB_API_KEY", "")
VECTOR_DB_ENVIRONMENT = os.getenv("VECTOR_DB_ENVIRONMENT", "")

# File type patterns
PDF_PATTERN = "*.pdf"
TEXT_PATTERN = "*.txt"
MARKDOWN_PATTERN = "*.md"
CSV_PATTERN = "*.csv"
HTML_PATTERN = "*.html"
RTF_PATTERN = "*.rtf"
DOCX_PATTERN = "*.docx"

# Medical terminology sources
UMLS_API_KEY = os.getenv("UMLS_API_KEY", "")
SNOMED_CT_PATH = os.getenv("SNOMED_CT_PATH", "")
RXNORM_PATH = os.getenv("RXNORM_PATH", "")

# AI Models
MEDICAL_NER_MODEL = "emilyalsentzer/Bio_ClinicalBERT"
SYMPTOM_CLASSIFIER_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2" 