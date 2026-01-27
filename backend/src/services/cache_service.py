import json
import hashlib


class CacheService:
    """Service for caching API responses in KV."""

    # TTL in seconds
    SEARCH_TTL = 3600  # 1 hour
    EXPLAIN_TTL = 86400  # 24 hours

    def __init__(self, kv):
        self.kv = kv

    def _make_key(self, prefix: str, value: str) -> str:
        """Generate a cache key from prefix and value."""
        normalized = value.lower().strip()
        hash_suffix = hashlib.md5(normalized.encode()).hexdigest()[:8]
        return f"{prefix}:{hash_suffix}"

    async def get_search(self, query: str) -> dict | None:
        """Get cached search results."""
        key = self._make_key("search", query)
        cached = await self.kv.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_search(self, query: str, results: dict) -> None:
        """Cache search results."""
        key = self._make_key("search", query)
        await self.kv.put(key, json.dumps(results), expiration_ttl=self.SEARCH_TTL)

    async def get_explain(self, query: str, matches_hash: str) -> dict | None:
        """Get cached explanation."""
        key = self._make_key("explain", f"{query}:{matches_hash}")
        cached = await self.kv.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_explain(self, query: str, matches_hash: str, result: dict) -> None:
        """Cache explanation."""
        key = self._make_key("explain", f"{query}:{matches_hash}")
        await self.kv.put(key, json.dumps(result), expiration_ttl=self.EXPLAIN_TTL)
