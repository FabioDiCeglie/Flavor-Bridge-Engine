from workers import Response


async def health_check() -> Response:
    return Response(None, status=204)

