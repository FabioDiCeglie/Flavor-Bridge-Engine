import json
from workers import Response
from services import AIService
from prompts import build_explain_prompt


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

        prompt = build_explain_prompt(query, matches)

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
