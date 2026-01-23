"""
AIService - Thin wrapper for Workers AI operations.

Responsibilities:
- LLM text generation
- Embedding generation
"""

LLM_MODEL = "@cf/meta/llama-3.1-8b-instruct"
EMBEDDING_MODEL = "@cf/baai/bge-small-en-v1.5"


class AIService:
    """Service layer for AI operations."""

    def __init__(self, ai):
        """
        Initialize with Cloudflare AI binding.

        Args:
            ai: Workers AI binding (env.AI)
        """
        self.ai = ai

    async def generate(self, prompt: str, max_tokens: int = 256) -> str:
        """
        Generate text from a prompt (LLM).

        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens in response

        Returns:
            Generated text response
        """
        response = await self.ai.run(
            LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return response.response

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: String to embed

        Returns:
            Embedding vector (384 dimensions)
        """
        response = await self.ai.run(EMBEDDING_MODEL, text=text)
        return list(response.data[0])

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of strings to embed

        Returns:
            List of embedding vectors (384 dimensions each)
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings
