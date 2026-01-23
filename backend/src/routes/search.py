import js
import json
from workers import Response
from services import VectorizeService


async def search(env, request) -> Response:
    """Search for similar ingredients (chemical cousins)."""
    try:
        url = js.URL.new(request.url)
        query = url.searchParams.get("q")
        query_lower = query.lower()
        
        if not query:
            return Response(
                json.dumps({"error": "Missing query parameter: ?q=ingredient"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )
        
        service = VectorizeService(env.AI, env.VECTORIZE)
        
        # Generate embedding for the query
        embedding = await service.generate_embedding(query)
        
        # Find similar vectors
        matches = await service.query(embedding)
        
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

        return Response(
            json.dumps({"query": query, "matches": results}),
            headers={"Content-Type": "application/json"},
        )
        
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
