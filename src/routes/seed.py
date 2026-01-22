import json
from workers import Response
from services import VectorizeService
from data import INGREDIENTS


async def seed(env) -> Response:
    """Seed the Vectorize database with ingredient embeddings."""
    try:
        service = VectorizeService(env.AI, env.VECTORIZE)
        count = await service.embed_and_upsert(INGREDIENTS)

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
