import js
import json
from workers import Response
from services import AIService, VectorizeService
from data import INGREDIENTS

BATCH_SIZE = 40  # Stay under 50 subrequests limit


async def seed(env, request) -> Response:
    """
    Seed the Vectorize database with ingredient embeddings.
    
    Query params:
        start: Starting index (default 0)
        
    Call multiple times to seed all ingredients:
        /seed?start=0, /seed?start=40, /seed?start=80, ...
    """
    try:
        url = js.URL.new(request.url)
        start = int(url.searchParams.get("start") or 0)
        
        # Get batch of ingredients
        batch = INGREDIENTS[start:start + BATCH_SIZE]
        
        if not batch:
            return Response(
                json.dumps({"success": True, "message": "No more ingredients to seed", "total": len(INGREDIENTS)}),
                headers={"Content-Type": "application/json"},
            )
        
        ai_service = AIService(env.AI)
        vectorize_service = VectorizeService(env.VECTORIZE, ai_service)
        
        count = await vectorize_service.embed_and_upsert(batch, start_id=start)
        
        next_start = start + BATCH_SIZE
        has_more = next_start < len(INGREDIENTS)

        return Response(
            json.dumps({
                "success": True,
                "seeded": count,
                "start": start,
                "next": next_start if has_more else None,
                "total": len(INGREDIENTS),
                "progress": f"{min(next_start, len(INGREDIENTS))}/{len(INGREDIENTS)}"
            }),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
