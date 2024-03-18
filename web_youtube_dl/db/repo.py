import typing as t
import uuid

import arrow
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Download, Request, RequestStatus


class RequestRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(self, url: str):
        drepo = DownloadRepo(self.session)
        if download := await drepo.get_download(url):
            request = Request(download=download, download_url=url)
        else:
            download = await drepo.create_download(url)
            request = Request(
                download=download, download_url=url, status=RequestStatus.PENDING
            )
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_request(self, id: uuid.UUID) -> t.Optional[Request]:
        return await self.session.get(Request, id)

    async def complete_request(self, request: Request, audio: bytes | None = None):
        if audio is not None:
            request.download.audio = audio
        request.completed_at = arrow.utcnow()
        request.progress = 100
        request.status = RequestStatus.COMPLETED
        self.session.add(request)
        await self.session.commit()

    async def update_downloading_request(self, id: uuid.UUID, progress: int):
        request = await self.get_request(id)
        assert request
        request.progress = progress
        request.status = RequestStatus.DOWNLOADING
        self.session.add(request)
        await self.session.commit()

    async def complete_downloading_request(self, id: uuid.UUID):
        request = await self.get_request(id)
        assert request
        request.progress = 99
        self.session.add(request)
        await self.session.commit()


class DownloadRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_download(self, url: str) -> t.Optional[Download]:
        return await self.session.get(Download, url)

    async def create_download(self, url: str) -> Download:
        dl = Download(url=url)
        self.session.add(dl)
        await self.session.commit()
        await self.session.refresh(dl)
        return dl
