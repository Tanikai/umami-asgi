from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.config import Config
from starlette.routing import Route

from umami_asgi import UmamiMiddleware

config = Config()
UMAMI_API_ENDPOINT = config('UMAMI_API_ENDPOINT')
UMAMI_SITE_ID = config('UMAMI_SITE_ID')

print(f"UMAMI_API_ENDPOINT: {UMAMI_API_ENDPOINT}")


async def homepage(request):
    return JSONResponse({'hello': 'world'})


async def feed(request):
    return JSONResponse({'posts': []})


app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/feed', feed, methods=['GET', 'POST']),
], middleware=[
    Middleware(UmamiMiddleware, api_endpoint=UMAMI_API_ENDPOINT, website_id=UMAMI_SITE_ID),
])
