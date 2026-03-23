import faiss
import json
import numpy as np

from app.config import settings

class SimilarityService:

    def __init__(self):
        print("Loading FAISS index...")

        # Load FAISS index
        self.index = faiss.read_index(settings.FAISS_INDEX_PATH)

        # Load metadata
        with open(settings.METADATA_PATH, "r") as f:
            self.metadata = json.load(f)

        print(f"FAISS index loaded with {self.index.ntotal} cards.")

    def search(self, embedding: np.ndarray, top_k: int = 5) -> list:
        # Reshape to 2D array for FAISS
        query = embedding.reshape(1, -1).astype("float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(query)

        # Search index
        scores, indices = self.index.search(query, top_k)

        # Map results to metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            card = self.metadata[idx]
            results.append({
                "id": card.get("id"),
                "name": card.get("name"),
                "set": card.get("set"),
                "types": card.get("types"),
                "rarity": card.get("rarity"),
                "image_url": card.get("image_url"),
                "score": float(score)
            })

        return results