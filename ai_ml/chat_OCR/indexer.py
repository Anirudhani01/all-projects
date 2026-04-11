# indexer.py
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class Indexer:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def create_index(self, chunks_json_path: str, index_output_path: str):
        """
        Creates a FAISS vector index from chunked JSON.
        Index is saved locally as .faiss and vectors.npy.
        """
        with open(chunks_json_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        embeddings = self.model.encode(chunks, convert_to_numpy=True)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        faiss.write_index(index, index_output_path)

        # Save chunks separately
        np.save(index_output_path.replace(".faiss", "_vectors.npy"), embeddings)

        return index
