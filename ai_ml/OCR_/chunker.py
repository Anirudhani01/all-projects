"""Content chunking module for PDF extracted content"""
import logging
import os
import json
from typing import List, Dict, Any
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Chunker:
    """Split extracted content into semantic chunks"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the Chunker with configurable parameters
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        logger.info(f"Chunker initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def chunk_text(self, text_data: List[Dict], source_doc: str = "unknown") -> List[Dict[str, Any]]:
        """
        Chunk text content with overlap
        
        Args:
            text_data: List of dicts with {"page": int, "text": str}
            source_doc: Source document name for metadata
            
        Returns:
            List of chunks with metadata
            Format: [{"chunk_id": str, "content": str, "content_type": str, 
                     "source_doc": str, "page": int, "metadata": dict}, ...]
        """
        chunks = []
        
        for text_item in text_data:
            page = text_item.get("page", 0)
            text = text_item.get("text", "")
            
            if not text.strip():
                continue
            
            try:
                # Split text into chunks
                text_chunks = self.text_splitter.split_text(text)
                total_chunks = len(text_chunks)
                
                # Batch create chunk objects with metadata
                chunks.extend([
                    {
                        "chunk_id": str(uuid.uuid4()),
                        "content": chunk_text,
                        "content_type": "text",
                        "source_doc": source_doc,
                        "page": page,
                        "metadata": {
                            "chunk_index": idx,
                            "total_chunks_on_page": total_chunks
                        }
                    }
                    for idx, chunk_text in enumerate(text_chunks)
                ])
                
            except Exception as e:
                logger.error(f"Error chunking text from page {page}: {str(e)}")
                continue
        
        logger.info(f"Text chunking complete: {len(chunks)} total chunks created")
        return chunks

    def chunk_tables(self, table_data: List[Dict], source_doc: str = "unknown") -> List[Dict[str, Any]]:
        """
        Process tables as single chunks
        
        Args:
            table_data: List of dicts with {"page": int, "table_id": int, "csv_path": str}
            source_doc: Source document name for metadata
            
        Returns:
            List of table chunks with metadata
        """
        chunks = []
        
        for table_item in table_data:
            page = table_item.get("page", 0)
            table_id = table_item.get("table_id", 0)
            csv_path = table_item.get("csv_path", "")
            
            try:
                # Read CSV content
                with open(csv_path, 'r', encoding='utf-8') as f:
                    table_content = f.read()
                
                if not table_content.strip():
                    continue
                
                # Create single chunk for the entire table
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "content": table_content,
                    "content_type": "table",
                    "source_doc": source_doc,
                    "page": page,
                    "metadata": {
                        "table_id": table_id,
                        "csv_path": csv_path
                    }
                })
                
            except Exception as e:
                logger.error(f"Error chunking table {table_id} from page {page}: {str(e)}")
                continue
        
        logger.info(f"Table chunking complete: {len(chunks)} table chunks created")
        return chunks

    def chunk_images(self, image_data: List[Dict], source_doc: str = "unknown") -> List[Dict[str, Any]]:
        """
        Create chunks for images with metadata
        
        Args:
            image_data: List of dicts with {"page": int, "image_id": int, "image_path": str}
            source_doc: Source document name for metadata
            
        Returns:
            List of image chunks with metadata
        """
        chunks = []
        
        for image_item in image_data:
            page = image_item.get("page", 0)
            image_id = image_item.get("image_id", 0)
            image_path = image_item.get("image_path", "")
            
            try:
                # Create chunk with image reference
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "content": f"Image {image_id} from page {page} of {source_doc}",
                    "content_type": "image",
                    "source_doc": source_doc,
                    "page": page,
                    "metadata": {
                        "image_id": image_id,
                        "image_path": image_path
                    }
                })
                
            except Exception as e:
                logger.error(f"Error chunking image {image_id} from page {page}: {str(e)}")
                continue
        
        logger.info(f"Image chunking complete: {len(chunks)} image chunks created")
        return chunks

    def save_chunks(self, chunks: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save chunks to a JSON file
        
        Args:
            chunks: List of chunk dictionaries
            output_path: Path to save the JSON file
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save chunks to JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(chunks)} chunks to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving chunks to {output_path}: {str(e)}")
            raise
    
    def load_chunks(self, input_path: str) -> List[Dict[str, Any]]:
        """
        Load chunks from a JSON file
        
        Args:
            input_path: Path to the JSON file
            
        Returns:
            List of chunk dictionaries
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            logger.info(f"Loaded {len(chunks)} chunks from {input_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading chunks from {input_path}: {str(e)}")
            raise
