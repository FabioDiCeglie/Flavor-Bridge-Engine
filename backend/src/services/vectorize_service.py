"""
VectorizeService - Handles all vector database operations.

Responsibilities:
- Generate embeddings via Workers AI
- Insert/upsert vectors into Vectorize
- Query similar vectors
"""
import js
from pyodide.ffi import to_js

EMBEDDING_MODEL = "@cf/baai/bge-small-en-v1.5"


class VectorizeService:
    """Service layer for Vectorize operations."""
    
    def __init__(self, ai, vectorize):
        """
        Initialize with Cloudflare bindings.
        
        Args:
            ai: Workers AI binding (env.AI)
            vectorize: Vectorize binding (env.VECTORIZE)
        """
        self.ai = ai
        self.vectorize = vectorize
    
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: String to embed
            
        Returns:
            Embedding vector (384 dimensions)
        """
        response = await self.ai.run(EMBEDDING_MODEL, text=text)
        return list(response.data[0])
    
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of strings to embed
            
        Returns:
            List of embedding vectors (384 dimensions each)
        """
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    async def upsert(self, vectors: list) -> None:
        """
        Upsert vectors into Vectorize (insert or update if exists).
        
        Args:
            vectors: List of vector dicts {id, values}
        """
        # Python dicts → JS Objects (required by Vectorize binding)
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
    
    async def embed_and_upsert(self, items: list[dict]) -> int:
        """
        Embed descriptions and upsert (safe to run multiple times).
        
        Args:
            items: List of {id, name, description}
            
        Returns:
            Number of items upserted
        """
        texts = [item["description"] for item in items]
        embeddings = await self.generate_embeddings(texts)
        
        vectors = []
        for i, item in enumerate(items):
            vectors.append({
                "id": str(item["id"]),
                "values": embeddings[i],
                "metadata": {
                    "name": item["name"],
                    "description": item["description"]
                }
            })
        
        await self.upsert(vectors)
        return len(vectors)
