import json
from workers import Response
from services import AIService, VectorizeService
from data import INGREDIENTS


async def seed(env) -> Response:
    """Seed the Vectorize database with ingredient embeddings."""
    try:
        ai_service = AIService(env.AI)
        vectorize_service = VectorizeService(env.VECTORIZE, ai_service)
        
        count = await vectorize_service.embed_and_upsert(INGREDIENTS)

        return Response(
            json.dumps({"success": True, "message": f"Seeded {count} ingredients"}),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
