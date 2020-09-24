import asyncio

from fastapi import APIRouter, Form
from fastapi.responses import FileResponse
from web_youtube_dl.app.youtube_dl_helpers import download_file

router = APIRouter()


@router.post(
    "/", description="Trigger an asynchronous file download",
)
async def download(url: str = Form(...)):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, download_file, url)
