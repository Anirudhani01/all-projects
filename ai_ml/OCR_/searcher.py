"""Semantic search module for querying indexed content"""
import logging
from typing import List, Dict, Any
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Searcher:
    """Perform semantic search on indexed content"""
    
    def __init__(self, indexer):
        """
        Initialize the Searcher with an Indexer instance
        
        Args:
            indexer: Indexer instance with loaded index
        """
        self.indexer = indexer
        logger.info("Searcher initialized")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks using semantic similarity
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of results with chunk content, score, and metadata
            Format: [{"chunk": str, "score": float, "metadata": dict}, ...]
        """
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        if self.indexer.embeddings is None or not self.indexer.chunks:
            logger.error("No index loaded. Please index content first.")
            return []
        
        try:
            # Generate embedding for the query
            logger.info(f"Searching for: {query}")
            query_embedding = self.indexer.model.encode([query])[0]
            
            # Compute cosine similarity between query and all chunks
            similarities = self._cosine_similarity(query_embedding, self.indexer.embeddings)
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Format results
            results = []
            for idx in top_indices:
                chunk = self.indexer.chunks[idx]
                score = float(similarities[idx])
                
                result = {
                    "chunk": chunk.get("content", ""),
                    "score": score,
                    "metadata": {
                        "source_doc": chunk.get("source_doc", "unknown"),
                        "page": chunk.get("page", 0),
                        "content_type": chunk.get("content_type", "unknown"),
                        "chunk_id": chunk.get("chunk_id", ""),
                        **chunk.get("metadata", {})
                    }
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def _cosine_similarity(self, query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between query and all embeddings
        
        Args:
            query_embedding: Query embedding vector
            embeddings: Matrix of all chunk embeddings
            
        Returns:
            Array of similarity scores
        """
        # Normalize vectors
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Compute cosine similarity
        similarities = np.dot(embeddings_norm, query_norm)
        
        return similarities
