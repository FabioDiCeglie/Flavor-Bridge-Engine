import json
from workers import Response
from services import AIService


async def explain(env, request) -> Response:
    """Explain why ingredients are chemical cousins using AI."""
    try:
        text = await request.text()
        body = json.loads(text)
        query = body.get("query")
        matches = body.get("matches")

        if not query or not matches:
            return Response(
                json.dumps({"error": "Missing 'query' or 'matches' in request body"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        # Build context from matches
        matches_context = "\n".join(
            f"- {m['name']}: {m['description']}"
            for m in matches[:3]
        )

        prompt = f"""You are a culinary scientist explaining flavor connections between ingredients.

A user searched for "{query}" and found these similar ingredients (ranked by chemical similarity):

{matches_context}

Explain WHY these ingredients are "chemical cousins" to {query}. Focus on:
1. Shared flavor compounds (glutamates, fermentation byproducts, etc.)
2. The science behind the similarity (amino acids, Maillard reaction, etc.)
3. A practical cooking tip for substitution

Keep it concise (2-3 sentences max) and accessible to home cooks."""

        service = AIService(env.AI)
        explanation = await service.generate(prompt)

        return Response(
            json.dumps({"query": query, "explanation": explanation}),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
