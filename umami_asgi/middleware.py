import httpx
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from .umami_api import UmamiRequest, UmamiPayload
from starlette.requests import Request
from starlette.responses import Response
from starlette.background import BackgroundTask
from dataclasses import asdict
from typing import List


async def send_umami_payload(
        api_endpoint: str,
        request_payload: UmamiRequest,
        headers: MutableHeaders,
        follow_redirects: bool
):
    async with httpx.AsyncClient() as client:
        try:
            payload = asdict(request_payload)
            await client.post(
                api_endpoint,
                json=payload,
                headers=headers,
                follow_redirects=follow_redirects
            )
        except Exception as e:
            # FIXME: How to do exception handling?
            print(f"Error sending umami payload: {e}")


class UmamiMiddleware(BaseHTTPMiddleware):

    def __init__(self,
                 app: ASGIApp,
                 api_endpoint: str,
                 website_id: str,
                 follow_redirects: bool = True,
                 proxy_enabled: bool = False,
                 trusted_proxies: List[str] = None,
                 ) -> None:
        super().__init__(app)
        self.app = app
        if not api_endpoint.endswith('/'):
            api_endpoint += '/'
        self.api_endpoint = api_endpoint + 'send'
        self.website_id = website_id
        self.follow_redirects = follow_redirects

        if proxy_enabled and trusted_proxies:
            self.trusted_proxies = set(trusted_proxies)
        else:
            self.trusted_proxies = None

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # create umami payload with request data
        umami_request = UmamiRequest(
            payload=UmamiPayload(
                hostname=request.url.hostname,
                language=request.headers.get('Accept-Language', ''),
                referrer=request.headers.get('Referer', ''),
                screen='',
                title='',
                url=request.url.path,
                website=self.website_id,
                ip=request.headers.get('X-Real-IP', request.client.host)
            )
        )

        # set headers to track IP address correctly
        umami_headers = MutableHeaders()
        # send proper user agent or request won't be registered
        umami_headers['User-Agent'] = request.headers.get('User-Agent', '')
        # send IP address of client, not asgi server
        umami_headers['X-Forwarded-Proto'] = 'https'

        # if trusted proxies is enabled and the sender's IP is in our trusted proxy list, we can trust the headers
        if self.trusted_proxies and (request.client.host in self.trusted_proxies or "0.0.0.0" in self.trusted_proxies):
            umami_headers['X-Real-IP'] = request.headers.get('X-Real-IP', request.client.host)
            umami_headers['X-Forwarded-For'] = request.headers.get('X-Forwarded-For', request.client.host)
            umami_headers['X-Forwarded-Host'] = request.headers.get('X-Forwarded-Host', request.url.hostname)

        else:
            # check against trusted proxies is disabled, so we have to assume that an attacker sends any headers
            # -> do not use any headers
            umami_headers['X-Real-IP'] = request.client.host
            umami_headers['X-Forwarded-For'] = request.client.host
            umami_headers['X-Forwarded-Host'] = ""

        response.background = BackgroundTask(
            send_umami_payload,
            self.api_endpoint,
            umami_request, umami_headers,
            self.follow_redirects
        )

        return response
