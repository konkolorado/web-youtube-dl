import asyncio

from fastapi import APIRouter, Form
from fastapi.responses import FileResponse
from web_youtube_dl.app.models import DownloadRequest
from web_youtube_dl.app.youtube_dl_helpers import download_file

router = APIRouter()


@router.post(
    "/", description="Trigger an asynchronous file download",
)
async def download(dl_req: DownloadRequest):
    loop = asyncio.get_running_loop()
    filename = await loop.run_in_executor(None, download_file, dl_req.url)
    return {"filename": filename}
