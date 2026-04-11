"""Main RAG pipeline orchestrator"""
import logging
import os
from typing import List, Dict, Any
from extractors.extractor_text import TextExtractor
from extractors.extractor_tables import TableExtractor
from extractors.extractor_images import ImageExtractor
from chunker import Chunker
from indexer import Indexer
from searcher import Searcher
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrate the complete RAG pipeline"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None, 
                 embedding_model: str = None):
        """
        Initialize the RAG pipeline
        
        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
            embedding_model: Embedding model name (default from config)
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        self.embedding_model = embedding_model or config.EMBEDDING_MODEL
        
        # Initialize components
        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.image_extractor = ImageExtractor()
        self.chunker = Chunker(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        self.indexer = Indexer(model_name=self.embedding_model)
        self.searcher = Searcher(self.indexer)
        
        logger.info("RAG Pipeline initialized")
    
    def process_pdf(self, pdf_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Process a PDF file through extraction and chunking
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory for extracted tables and images (default from config)
            
        Returns:
            Dictionary with extracted and chunked content
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        output_dir = output_dir or config.OUTPUT_DIR
        text_dir = os.path.join(output_dir, "text")
        tables_dir = os.path.join(output_dir, "tables")
        images_dir = os.path.join(output_dir, "images")
        chunks_dir = os.path.join(output_dir, "chunks")
        
        # Create output directories
        os.makedirs(text_dir, exist_ok=True)
        os.makedirs(tables_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(chunks_dir, exist_ok=True)
        
        pdf_filename = os.path.basename(pdf_path)
        logger.info(f"Processing PDF: {pdf_filename}")
        
        # Extract content
        logger.info("Step 1: Extracting text...")
        text_data = self.text_extractor.extract(pdf_path, text_dir)
        
        logger.info("Step 2: Extracting tables...")
        table_data = self.table_extractor.extract(pdf_path, tables_dir)
        
        logger.info("Step 3: Extracting images...")
        image_data = self.image_extractor.extract(pdf_path, images_dir)
        
        # Chunk content
        logger.info("Step 4: Chunking content...")
        text_chunks = self.chunker.chunk_text(text_data, source_doc=pdf_filename)
        table_chunks = self.chunker.chunk_tables(table_data, source_doc=pdf_filename)
        image_chunks = self.chunker.chunk_images(image_data, source_doc=pdf_filename)
        
        # Combine all chunks
        all_chunks = text_chunks + table_chunks + image_chunks
        
        # Save chunks to JSON file
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        chunks_file = os.path.join(chunks_dir, f"{pdf_name}_chunks.json")
        self.chunker.save_chunks(all_chunks, chunks_file)
        
        logger.info(f"Processing complete: {len(all_chunks)} total chunks created")
        
        return {
            "pdf_path": pdf_path,
            "chunks": all_chunks,
            "chunks_file": chunks_file,
            "stats": {
                "text_chunks": len(text_chunks),
                "table_chunks": len(table_chunks),
                "image_chunks": len(image_chunks),
                "total_chunks": len(all_chunks)
            }
        }

    def build_index(self, chunks: List[Dict] = None, pdf_path: str = None) -> Dict[str, Any]:
        """
        Build index from chunks or by processing a PDF
        
        Args:
            chunks: Pre-processed chunks (optional)
            pdf_path: Path to PDF to process (optional)
            
        Returns:
            Dictionary with indexing statistics
        """
        if chunks is None and pdf_path is None:
            logger.error("Either chunks or pdf_path must be provided")
            raise ValueError("Either chunks or pdf_path must be provided")
        
        # Process PDF if path provided
        if pdf_path:
            result = self.process_pdf(pdf_path)
            chunks = result["chunks"]
        
        # Index chunks
        logger.info(f"Building index for {len(chunks)} chunks...")
        self.indexer.index_chunks(chunks)
        
        # Get statistics
        stats = self.indexer.get_statistics()
        logger.info(f"Index built successfully: {stats}")
        
        return stats
    
    def query(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search the indexed content
        
        Args:
            query: Search query string
            top_k: Number of results to return (default from config)
            
        Returns:
            List of search results with scores and metadata
        """
        top_k = top_k or config.DEFAULT_TOP_K
        
        logger.info(f"Querying: {query}")
        results = self.searcher.search(query, top_k=top_k)
        
        return results
    
    def save_index(self, index_path: str = None) -> None:
        """
        Save the current index to disk
        
        Args:
            index_path: Path to save index (default from config)
        """
        index_path = index_path or config.INDEX_FILE
        logger.info(f"Saving index to {index_path}")
        self.indexer.save_index(index_path)
    
    def load_index(self, index_path: str = None) -> None:
        """
        Load an existing index from disk
        
        Args:
            index_path: Path to index file (default from config)
        """
        index_path = index_path or config.INDEX_FILE
        logger.info(f"Loading index from {index_path}")
        self.indexer.load_index(index_path)
    
    def process_and_index_pdf(self, pdf_path: str, save_index: bool = True) -> Dict[str, Any]:
        """
        Complete pipeline: process PDF and build index
        
        Args:
            pdf_path: Path to PDF file
            save_index: Whether to save index to disk
            
        Returns:
            Dictionary with processing and indexing statistics
        """
        logger.info(f"Running complete pipeline for {pdf_path}")
        
        # Process PDF
        process_result = self.process_pdf(pdf_path)
        
        # Build index
        index_stats = self.build_index(chunks=process_result["chunks"])
        
        # Save index if requested
        if save_index:
            self.save_index()
        
        return {
            "processing": process_result["stats"],
            "indexing": index_stats
        }
