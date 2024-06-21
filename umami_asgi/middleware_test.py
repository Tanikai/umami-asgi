import pytest
from pytest_httpx import HTTPXMock

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from umami_asgi.middleware import UmamiMiddleware
from starlette.testclient import TestClient
from json import loads


async def feed(request: Request) -> PlainTextResponse:
    return PlainTextResponse("New posts")


async def homepage(request: Request) -> PlainTextResponse:
    return PlainTextResponse("Hello, world")


@pytest.mark.asyncio
async def test_analytics_post(httpx_mock: HTTPXMock):
    httpx_mock.add_response()
    app = Starlette(
        routes=[
            Route("/", endpoint=homepage),
            Route("/feed", endpoint=feed, methods=["GET", "POST"]),
        ],
        middleware=[
            Middleware(UmamiMiddleware, api_endpoint="https://localhost/api", website_id="123456"),
        ],
    )

    with TestClient(app, base_url="http://testserver") as client:
        response = client.get("/")
        assert response.status_code == 200

        # check whether middleware sent post request to mocked umami
        umami_request = httpx_mock.get_request()
        umami_payload = loads(umami_request.content.decode("utf-8"))["payload"]
        assert umami_payload["name"] == "GET"
        assert umami_payload["url"] == "/"
        # check whether middleware set headers correctly to track IP address of client, not asgi server
        assert umami_request.headers["X-Real-IP"] == "testclient"
        assert umami_request.headers["X-Forwarded-For"] == "testclient"

        response = client.post("/feed")
        assert response.status_code == 200

        umami_request = httpx_mock.get_requests()[1]
        umami_payload = loads(umami_request.content.decode("utf-8"))["payload"]
        assert umami_payload["name"] == "POST"
        assert umami_payload["url"] == "/feed"
