"""Configuration settings for PDF RAG Pipeline"""
import os

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Output directories
OUTPUT_DIR = "output"
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
CHUNKS_DIR = os.path.join(OUTPUT_DIR, "chunks")
INDEX_DIR = os.path.join(OUTPUT_DIR, "index")

# Index file path
INDEX_FILE = os.path.join(INDEX_DIR, "vector_index.pkl")

# Search settings
DEFAULT_TOP_K = 5
