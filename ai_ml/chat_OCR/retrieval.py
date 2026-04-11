# retrieval.py
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, index_path: str, chunks_json_path: str, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = faiss.read_index(index_path)

        with open(chunks_json_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

    def query(self, question: str, top_k=3):
        """
        Searches the FAISS vector index for top_k relevant chunks.
        """
        query_embedding = self.model.encode([question], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            results.append({
                "score": float(score),
                "content": self.chunks[idx]
            })

        return results
