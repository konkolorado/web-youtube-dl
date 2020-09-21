import asyncio
import logging
import urllib

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from werkzeug.utils import secure_filename

from web_youtube_dl.app.utils import download_path
from web_youtube_dl.app.youtube_dl_helpers import download_file

logger = logging.getLogger("web-youtube-dl")
router = APIRouter()


@router.post(
    "/", description="Trigger an asynchronous file download",
)
async def download(url: str = Form(...)):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, download_file, url)


@router.get("/downloads/{filename}", description="Download a file by its filename")
async def retrieve(filename: str):
    filename = urllib.parse.unquote(filename)
    # filename = secure_filename(filename)
    try:
        return FileResponse(
            download_path() + filename, filename=filename, media_type="audio/mpeg",
        )
    except FileNotFoundError as e:
        logger.exception(f"Unable to send file: {e}")
        raise HTTPException(status_code=404, detail="Item not found")
