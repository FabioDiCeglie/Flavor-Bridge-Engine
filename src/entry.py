from workers import Response, Request


async def on_fetch(request: Request) -> Response:
    return Response("Hello from Flavor Bridge Engine! 🧪🍳")

