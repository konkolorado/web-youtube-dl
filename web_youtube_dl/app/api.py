import asyncio
import logging

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from web_youtube_dl.services import progress, youtube

logger = logging.getLogger(__name__)

router = APIRouter()


class DownloadRequest(BaseModel):
    url: HttpUrl


class DownloadResponse(BaseModel):
    filename: str


@router.post(
    "/",
    description="Trigger an asynchronous file download",
    response_model=DownloadResponse,
)
async def download(req: DownloadRequest):
    logger.debug(f"Received download request {req}")
    queues = progress.ProgressQueues()
    ytd = youtube.YTDownload(req.url, queues)
    queues.track(ytd.filename)
    logger.debug(f"Tracking download for {req.url} as {ytd.filename}")

    dlm = youtube.DownloadManager()
    loop = asyncio.get_running_loop()
    filepath = await loop.run_in_executor(None, dlm.download, ytd)
    return {"filename": filepath.name}
