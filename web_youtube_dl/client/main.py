import uuid
from contextlib import AsyncExitStack

import httpx

import web_youtube_dl
from web_youtube_dl.app.main import app
from web_youtube_dl.client.responses import DownloadResponse
from web_youtube_dl.config import DEFAULT_EPHEMERAL_HOST, DEFAULT_EPHEMERAL_PORT


def transport_for_app():
    return httpx.ASGITransport(
        app=app,  # type: ignore
        client=(DEFAULT_EPHEMERAL_HOST, DEFAULT_EPHEMERAL_PORT),
    )


class DownloadClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        port: int | None = None,
        headers: dict | None = None,
    ) -> None:
        self._base_url = base_url
        self._port = port
        self._headers = headers or {"APP_VERSION": web_youtube_dl.__version__}

    @property
    def port(self) -> int:
        return self._port if self._port else DEFAULT_EPHEMERAL_PORT

    @property
    def base_url(self) -> str | None:
        return self._base_url if self._base_url else DEFAULT_EPHEMERAL_HOST

    @property
    def url(self) -> str:
        return f"{self.base_url}:{self.port}"

    async def __aenter__(self) -> "DownloadClient":
        if (
            self.base_url == DEFAULT_EPHEMERAL_HOST
            and self.port == DEFAULT_EPHEMERAL_PORT
        ):
            transport = transport_for_app()
        else:
            transport = None

        self._exit_stack = AsyncExitStack()
        self.client = await self._exit_stack.enter_async_context(
            httpx.AsyncClient(transport=transport)
        )
        return self

    async def __aexit__(self, *exc):
        return

    async def start_download(
        self, url: str, *, headers: dict | None = None
    ) -> DownloadResponse:
        response = await self.client.post(f"{self.url}/api/", json={"url": url})
        return response.json()

    async def get_download_status(
        self, request_id: str | uuid.UUID, *, headers: dict | None = None
    ) -> DownloadResponse:
        response = await self.client.get(f"{self.url}/api/{request_id}/status")
        return response.json()

    async def get_download(
        self, request_id: str | uuid.UUID, *, headers: dict | None = None
    ):
        response = await self.client.get(f"{self.url}/api/{request_id}")
        return response.json()
