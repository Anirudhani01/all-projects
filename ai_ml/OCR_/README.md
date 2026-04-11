# PDF RAG Pipeline

A modular system for extracting, chunking, indexing, and searching PDF documents using RAG (Retrieval-Augmented Generation) techniques.

## Features

- Extract text, tables, and images from PDFs
- Semantic chunking with configurable overlap
- Vector embeddings using sentence-transformers
- File-based storage (no database required)
- Semantic search with similarity scoring

## Installation

```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── extractors/          # PDF content extractors
├── chunker.py          # Content chunking module
├── indexer.py          # Vector indexing module
├── searcher.py         # Semantic search module
├── pipeline.py         # Main pipeline orchestrator
├── config.py           # Configuration settings
├── utils.py            # Helper utilities
└── example.py          # Usage examples
```

## Usage

See `example.py` for complete usage examples.
