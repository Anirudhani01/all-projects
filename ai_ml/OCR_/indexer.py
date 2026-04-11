"""Vector indexing module for semantic search"""
import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Indexer:
    """Generate embeddings and build searchable index"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Indexer with a sentence transformer model
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Model loaded successfully")
        
        # Storage for embeddings and chunks
        self.embeddings = None
        self.chunks = []
        self.index_metadata = {
            "model_name": model_name,
            "created_at": None,
            "total_chunks": 0
        }
    
    def index_chunks(self, chunks: List[Dict]) -> None:
        """
        Generate embeddings for all chunks and build index
        
        Args:
            chunks: List of chunk dictionaries with content and metadata
        """
        if not chunks:
            logger.warning("No chunks provided for indexing")
            return
        
        logger.info(f"Indexing {len(chunks)} chunks...")
        
        # Extract content from chunks for embedding
        contents = [chunk.get("content", "") for chunk in chunks]
        
        try:
            # Generate embeddings for all chunks
            embeddings = self.model.encode(contents, show_progress_bar=True)
            
            # Store embeddings as numpy array
            self.embeddings = np.array(embeddings)
            
            # Store chunks (without embeddings to save space)
            self.chunks = chunks
            
            # Update metadata
            self.index_metadata["created_at"] = datetime.now().isoformat()
            self.index_metadata["total_chunks"] = len(chunks)
            
            logger.info(f"Indexing complete: {len(chunks)} chunks indexed")
            logger.info(f"Embedding shape: {self.embeddings.shape}")
            
        except Exception as e:
            logger.error(f"Error during indexing: {str(e)}")
            raise

    def save_index(self, index_path: str) -> None:
        """
        Save index to disk using pickle
        
        Args:
            index_path: Path to save the index file
        """
        import pickle
        import os
        
        if self.embeddings is None or not self.chunks:
            logger.warning("No index to save. Please run index_chunks() first.")
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            
            # Prepare index data
            index_data = {
                "embeddings": self.embeddings,
                "chunks": self.chunks,
                "metadata": self.index_metadata
            }
            
            # Save to disk
            with open(index_path, 'wb') as f:
                pickle.dump(index_data, f)
            
            logger.info(f"Index saved successfully to {index_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, index_path: str) -> None:
        """
        Load index from disk
        
        Args:
            index_path: Path to the index file
        """
        import pickle
        import os
        
        if not os.path.exists(index_path):
            logger.error(f"Index file not found: {index_path}")
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        try:
            # Load from disk
            with open(index_path, 'rb') as f:
                index_data = pickle.load(f)
            
            # Restore index data
            self.embeddings = index_data["embeddings"]
            self.chunks = index_data["chunks"]
            self.index_metadata = index_data["metadata"]
            
            logger.info(f"Index loaded successfully from {index_path}")
            logger.info(f"Loaded {len(self.chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise

    def add_chunks(self, new_chunks: List[Dict]) -> None:
        """
        Add new chunks to existing index without rebuilding
        
        Args:
            new_chunks: List of new chunk dictionaries to add
        """
        if not new_chunks:
            logger.warning("No new chunks provided")
            return
        
        logger.info(f"Adding {len(new_chunks)} new chunks to index...")
        
        try:
            # Extract content from new chunks
            contents = [chunk.get("content", "") for chunk in new_chunks]
            
            # Generate embeddings for new chunks
            new_embeddings = self.model.encode(contents, show_progress_bar=True)
            new_embeddings = np.array(new_embeddings)
            
            # Append to existing embeddings
            if self.embeddings is None:
                self.embeddings = new_embeddings
                self.chunks = new_chunks
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
                self.chunks.extend(new_chunks)
            
            # Update metadata
            self.index_metadata["total_chunks"] = len(self.chunks)
            
            logger.info(f"Successfully added {len(new_chunks)} chunks. Total chunks: {len(self.chunks)}")
            
        except Exception as e:
            logger.error(f"Error adding chunks to index: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed content
        
        Returns:
            Dictionary with statistics about the index
        """
        if not self.chunks:
            return {
                "total_chunks": 0,
                "content_types": {},
                "model_name": self.model_name,
                "created_at": None
            }
        
        # Count content types
        content_types = {}
        for chunk in self.chunks:
            content_type = chunk.get("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        stats = {
            "total_chunks": len(self.chunks),
            "content_types": content_types,
            "model_name": self.model_name,
            "created_at": self.index_metadata.get("created_at"),
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0
        }
        
        return stats
