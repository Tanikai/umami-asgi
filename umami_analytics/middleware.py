import httpx
from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from .umami_api import UmamiPayload
from starlette.requests import Request
from starlette.responses import Response
from starlette.background import BackgroundTask
from dataclasses import asdict


async def send_umami_payload(api_endpoint: str, payload: UmamiPayload, headers: MutableHeaders):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(api_endpoint, json=asdict(payload), headers=headers)
        except Exception as e:
            # FIXME: How to do exception handling?
            print(f"Error sending umami payload: {e}")


class UmamiMiddleware(BaseHTTPMiddleware):

    def __init__(self,
                 app: ASGIApp,
                 api_endpoint: str,
                 token: str,
                 website_id: str,
                 ) -> None:
        super().__init__(app)
        self.app = app
        if not api_endpoint.endswith('/'):
            api_endpoint += '/'
        self.api_endpoint = api_endpoint
        self.token = token
        self.website_id = website_id

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # create umami payload with request data
        payload = UmamiPayload(
            hostname=request.url.hostname,
            language=request.headers.get('Accept-Language', ''),
            referrer=request.headers.get('Referer', ''),
            screen='',
            title='',
            url=request.url.path,
            website=self.website_id,
            name=request.method,
        )

        # set headers to track IP address correctly
        umami_headers = MutableHeaders()
        umami_headers['X-Real-IP'] = request.client.host
        umami_headers['X-Forwarded-For'] = request.client.host
        response.background = BackgroundTask(send_umami_payload, self.api_endpoint, payload, umami_headers)

        return response
