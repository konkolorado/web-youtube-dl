import asyncio
import logging

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from web_youtube_dl.services import metadata, progress, youtube

logger = logging.getLogger(__name__)

router = APIRouter()
queues = progress.ProgressQueues()
mm = metadata.MetadataManager()
dlm = youtube.DownloadManager()


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
    logger.info(f"Handling download request {req}")
    ytd = youtube.YTDownload(req.url, pqs=queues)
    queues.track(ytd.filename)
    loop = asyncio.get_running_loop()
    filepath = await loop.run_in_executor(
        None, dlm.download_and_process, ytd, mm, queues
    )
    return {"filename": filepath.name}
