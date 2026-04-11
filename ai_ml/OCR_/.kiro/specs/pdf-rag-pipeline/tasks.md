# Implementation Plan

- [x] 1. Set up project structure and dependencies



  - Create directory structure for extractors, chunker, indexer, and searcher modules
  - Create requirements.txt with pymupdf, camelot-py, sentence-transformers, langchain, numpy
  - Create main configuration file for chunk sizes, model names, and paths
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2. Implement text extractor



  - [x] 2.1 Create extractor_text.py with TextExtractor class


    - Implement extract() method using PyMuPDF to extract text from all pages
    - Return list of dictionaries with page numbers and text content
    - Add error handling for corrupted PDFs or unreadable pages
    - _Requirements: 1.1, 1.4, 1.5_

- [x] 3. Implement table extractor





  - [ ] 3.1 Create extractor_tables.py with TableExtractor class
    - Implement extract() method using Camelot to detect and extract tables
    - Save each table as CSV file with naming convention: {pdf_name}_page{page}_table{id}.csv





    - Return list of dictionaries with page numbers, table IDs, and CSV paths
    - Add error handling for pages without tables or extraction failures
    - _Requirements: 1.2, 1.4, 1.5_






- [ ] 4. Implement image extractor
  - [ ] 4.1 Create extractor_images.py with ImageExtractor class
    - Implement extract() method using PyMuPDF to extract images from all pages
    - Save images with naming convention: {pdf_name}_page{page}_img{id}.{ext}


    - Return list of dictionaries with page numbers, image IDs, and image paths
    - Add error handling for pages without images or extraction failures
    - _Requirements: 1.3, 1.4, 1.5_




- [ ] 5. Implement chunker component
  - [ ] 5.1 Create chunker.py with Chunker class
    - Initialize with configurable chunk_size and chunk_overlap parameters

    - Implement chunk_text() method using LangChain RecursiveCharacterTextSplitter
    - Preserve page numbers and source document metadata in each chunk



    - _Requirements: 2.1, 2.2, 2.5_
  
  - [ ] 5.2 Add table chunking support
    - Implement chunk_tables() method that treats each table as a single chunk
    - Read CSV files and include table content with metadata
    - Preserve page numbers and CSV file references
    - _Requirements: 2.3, 2.5_
  
  - [ ] 5.3 Add image chunking support
    - Implement chunk_images() method that creates chunks with image references
    - Include image metadata and any associated captions
    - Preserve page numbers and image file paths
    - _Requirements: 2.4, 2.5_
  
  - [ ] 5.4 Add error handling for chunking
    - Handle empty content gracefully
    - Log errors for malformed chunks and continue processing
    - _Requirements: 2.5_

- [x] 6. Implement indexer component


  - [x] 6.1 Create indexer.py with Indexer class

    - Initialize sentence-transformers model (all-MiniLM-L6-v2)
    - Implement index_chunks() method to generate embeddings for all chunks
    - Store embeddings as numpy array with associated chunk metadata
    - _Requirements: 3.1, 3.2_
  
  - [x] 6.2 Add index persistence


    - Implement save_index() method using pickle to save embeddings and metadata
    - Implement load_index() method to load existing index from disk
    - Include index metadata (model name, creation timestamp)
    - _Requirements: 3.2_
  
  - [x] 6.3 Add incremental indexing support


    - Implement add_chunks() method to append new chunks to existing index
    - Update numpy arrays and metadata without rebuilding entire index
    - _Requirements: 3.3_
  
  - [x] 6.4 Add error handling and statistics


    - Handle embedding generation failures for individual chunks
    - Log errors and continue with remaining chunks
    - Return statistics about indexed content (total chunks, content types)
    - _Requirements: 3.4, 3.5_

- [x] 7. Implement searcher component



  - [x] 7.1 Create searcher.py with Searcher class


    - Initialize with reference to Indexer instance
    - Implement search() method that generates query embedding
    - Compute cosine similarity between query and all indexed chunks using numpy
    - Return top-k results sorted by similarity score
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 7.2 Add result formatting and metadata

    - Include chunk content, similarity score, and source metadata in results
    - Format metadata to show document name, page number, and content type
    - Handle empty result sets with appropriate messaging
    - _Requirements: 4.4, 4.5_

- [x] 8. Create main pipeline orchestrator



  - [x] 8.1 Create pipeline.py with RAGPipeline class


    - Implement process_pdf() method that orchestrates all extraction steps
    - Call all three extractors and aggregate results
    - Pass extracted content to chunker
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.3, 2.4_
  
  - [x] 8.2 Add pipeline methods for indexing and searching


    - Implement build_index() method that indexes all chunks
    - Implement query() method that performs search and returns formatted results
    - Add methods to save and load complete pipeline state
    - _Requirements: 3.1, 3.2, 4.1, 4.2, 4.3_

- [x] 9. Create example usage script



  - [x] 9.1 Create example.py demonstrating the full pipeline


    - Show how to process a PDF file
    - Demonstrate indexing the extracted content
    - Show example queries and result formatting
    - Include comments explaining each step
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 4.1_

- [ ] 10. Add configuration and utilities
  - [ ] 10.1 Create config.py with default settings
    - Define default chunk sizes, overlap, and model names
    - Define output directory paths for tables and images
    - Define index storage path
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 10.2 Create utils.py with helper functions
    - Add function to validate PDF file paths
    - Add function to create output directories if they don't exist
    - Add logging configuration utilities
    - _Requirements: 1.4, 2.5, 3.4_
