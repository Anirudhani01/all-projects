# Enhanced Page-by-Page PDF RAG Pipeline

## Overview
This project implements a comprehensive Retrieval Augmented Generation (RAG) pipeline for processing PDF documents page-by-page. It features advanced content extraction, cleaning, adaptive query strategies, and optimized storage in PostgreSQL with vector embeddings. The system is designed for high-quality document analysis, efficient retrieval, and flexible querying.

## Key Features
- **Page-level PDF processing**: Extracts and cleans content from each page individually.
- **Advanced text cleaning**: Removes headers, footers, and noise for high-quality data.
- **AI-powered chunking and categorization**: Uses LLMs to classify and split content into logical chunks.
- **PostgreSQL + pgvector storage**: Stores metadata, chunks, and embeddings for fast similarity search.
- **Adaptive RAG strategies**: Analyzes queries to select the best retrieval/generation approach (single-shot, multi-hop, synthesis).
- **Interactive CLI**: Supports interactive querying, statistics, and document/page exploration.

## Architecture
- **PDF Parsing**: Uses LlamaParse for page-by-page extraction and cleaning.
- **Content Analysis**: Classifies content and creates intelligent chunks using OpenAI models.
- **Database Management**: Optimized schema for documents, pages, and chunks; embeddings stored for retrieval.
- **Query Engine**: Adaptive strategies based on query analysis; supports both advanced and simple RAG modes.
- **Logging**: Enhanced logging system with colored terminal output and detailed file logs.

## Setup
1. **Clone the repository** and navigate to the project folder.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**:
   - Run:
     ```bash
     python rag_pipeline.py --create-env
     ```
   - Edit the generated `.env` file with your API keys and database connection details.
4. **Setup the database**:
   ```bash
   python rag_pipeline.py --setup
   ```

## Usage
### Process a PDF file
```bash
python rag_pipeline.py document.pdf
```

### Process all PDFs in a directory
```bash
python rag_pipeline.py documents/
```

### Query the database
```bash
python rag_pipeline.py --query "What is X?"
```

### Interactive mode
```bash
python rag_pipeline.py --interactive
```

### Show statistics
```bash
python rag_pipeline.py --stats
```

### Show page summary for a document
```bash
python rag_pipeline.py --page-summary <doc_id>
```

### Show content for a specific page
```bash
python rag_pipeline.py --page-content <doc_id> <page_num>
```

## Configuration
All settings are managed via the `.env` file. Key options include:
- `OPENAI_API_KEY`, `LLAMA_CLOUD_API_KEY`, `TAVILY_API_KEY`
- `DATABASE_URL` (PostgreSQL connection string)
- Model selection: `EMBEDDING_MODEL`, `CHAT_MODEL`, `ANALYSIS_MODEL`
- Processing options: `STORE_INDIVIDUAL_PAGES`, `ADVANCED_CLEANING`, `MAX_CHUNK_SIZE`, `CHUNK_OVERLAP`
- Adaptive RAG: `ADAPTIVE_RAG_ENABLED`, `MAX_RETRIEVAL_ATTEMPTS`, `CONFIDENCE_THRESHOLD`

## Advanced Features
- **Adaptive Query Analysis**: Classifies queries and selects optimal retrieval/generation strategy.
- **Page-aware Retrieval**: Answers reference specific pages and document sources.
- **Comprehensive Statistics**: Tracks document, page, and chunk metrics for analysis.
- **Interactive Exploration**: CLI supports stats, summaries, and direct page access.

## Requirements
- Python 3.8+
- PostgreSQL with pgvector extension
- API keys for OpenAI, LlamaCloud, and Tavily

## License
See `LICENSE` for details.

## Acknowledgements
- [LangChain](https://github.com/langchain-ai/langchain)
- [LlamaParse](https://llamaindex.ai/)
- [pgvector](https://github.com/pgvector/pgvector)

---
For more details, see comments and docstrings in `rag_pipeline.py`.
