import js
import json
from workers import Response
from services import AIService, VectorizeService, CacheService


async def search(env, request) -> Response:
    """Search for similar ingredients (chemical cousins)."""
    try:
        url = js.URL.new(request.url)
        query = url.searchParams.get("q")

        if not query:
            return Response(
                json.dumps({"error": "Missing query parameter: ?q=ingredient"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        query_lower = query.lower()

        # Check cache first
        cache_service = CacheService(env.CACHE)
        cached = await cache_service.get_search(query)
        if cached:
            return Response(
                json.dumps(cached),
                headers={"Content-Type": "application/json", "X-Cache": "HIT"},
            )

        ai_service = AIService(env.AI)
        vectorize_service = VectorizeService(env.VECTORIZE)

        # Generate embedding for the query
        embedding = await ai_service.embed(query)

        # Find similar vectors
        matches = await vectorize_service.query(embedding)

        results = []
        for match in matches:
            if match.metadata.name.lower() == query_lower:
                continue
            result = {
                "id": match.id,
                "score": match.score,
                "name": match.metadata.name,
                "description": match.metadata.description,
            }
            results.append(result)

        response_data = {"query": query, "matches": results}

        # Cache the results
        await cache_service.set_search(query, response_data)

        return Response(
            json.dumps(response_data),
            headers={"Content-Type": "application/json", "X-Cache": "MISS"},
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
