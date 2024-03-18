import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl

from web_youtube_dl.db import DownloadRepo, Request, RequestRepo, get_session
from web_youtube_dl.services import metadata, youtube

logger = logging.getLogger(__name__)

router = APIRouter()


class DownloadRequest(BaseModel):
    url: HttpUrl


async def _download(id: uuid.UUID):
    async with get_session() as session:
        requests = RequestRepo(session)
        if req := await requests.get_request(id):
            downloads = DownloadRepo(session)
            download = await downloads.get_download(req.download_url)
            if download is None or download.audio is None:
                ytd = youtube.YTDownload(req.download_url, id)
                await youtube.DownloadManager(ytd).download_and_process(
                    metadata.MetadataManager(), requests
                )
            else:
                await requests.complete_request(req)


async def create_and_begin_download(url: str, tasks: BackgroundTasks) -> Request:
    async with get_session() as session:
        requests = RequestRepo(session)
        request = await requests.create_request(url)
        assert request.id is not None

    tasks.add_task(_download, request.id)
    return request


async def get_download_request_or_404(session, req_id: uuid.UUID):
    requests = RequestRepo(session)
    if (request := await requests.get_request(req_id)) is None:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return request


@router.post("/", description="Trigger an async file download", response_model=Request)
async def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    return await create_and_begin_download(str(req.url), background_tasks)


@router.get(
    "/{req_id}/status",
    description="Retrieve a download's status",
    response_model=Request,
)
async def get_download_status(req_id: uuid.UUID):
    async with get_session() as session:
        data = await get_download_request_or_404(session, req_id)
        data.download.audio = None
        return data


@router.get("/{req_id}", description="Retrieve a downloaded file")
async def get_download(req_id: uuid.UUID):
    async with get_session() as session:
        data = await get_download_request_or_404(session, req_id)

    headers = {"Content-Disposition": f'attachment; filename="{data.download.url}"'}
    return Response(
        content=data.download.audio, media_type="audio/mpeg", headers=headers
    )
