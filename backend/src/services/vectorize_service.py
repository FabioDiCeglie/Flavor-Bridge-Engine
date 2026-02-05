"""
VectorizeService - Handles vector database operations.

Responsibilities:
- Upsert vectors into Vectorize
- Query similar vectors
"""
import js
from pyodide.ffi import to_js

from utils.helpers import format_ingredient_for_embedding, format_compounds


class VectorizeService:
    """Service layer for Vectorize operations."""

    def __init__(self, vectorize, ai_service=None):
        """
        Initialize with Cloudflare Vectorize binding.

        Args:
            vectorize: Vectorize binding (env.VECTORIZE)
            ai_service: Optional AIService for embed_and_upsert convenience method
        """
        self.vectorize = vectorize
        self.ai_service = ai_service

    async def upsert(self, vectors: list) -> None:
        """
        Upsert vectors into Vectorize (insert or update if exists).

        Args:
            vectors: List of vector dicts {id, values, metadata}
        """
        js_vectors = to_js(vectors, dict_converter=js.Object.fromEntries)
        await self.vectorize.upsert(js_vectors)

    async def query(self, vector: list[float], top_k: int = 6):
        """
        Query similar vectors.

        Args:
            vector: Query vector (384 dimensions)
            top_k: Number of results to return

        Returns:
            List of matches with scores and metadata
        """
        results = await self.vectorize.query(vector, topK=top_k, returnMetadata="all")
        return results.matches

    async def embed_and_upsert(self, items: list[dict], start_id: int = 0) -> int:
        """
        Embed descriptions and upsert (convenience method).

        Requires ai_service to be set in constructor.

        Args:
            items: List of {id, name, description}

        Returns:
            Number of items upserted
        """
        if not self.ai_service:
            raise ValueError("AIService required for embed_and_upsert")

        # Embed name + compounds for chemical similarity matching
        texts = [format_ingredient_for_embedding(item) for item in items]
        embeddings = await self.ai_service.embed_batch(texts)

        vectors = [
            {
                "id": str(start_id + i + 1),
                "values": embeddings[i],
                "metadata": {
                    "name": item["name"],
                    "description": item["description"],
                    "compounds": format_compounds(item),
                },
            }
            for i, item in enumerate(items)
        ]

        await self.upsert(vectors)
        return len(vectors)
