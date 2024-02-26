import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from web_youtube_dl.app.api import (
    DownloadRequest,
    create_and_begin_download,
    get_download_request_or_404,
)
from web_youtube_dl.config import get_static_path, get_templates_path
from web_youtube_dl.db import get_session

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=get_templates_path())


@router.get("/favicon.ico")
async def favicon():
    return FileResponse(f"{get_static_path()}/favicon.ico")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html.j2", {"request": request})


@router.post("/start", response_class=HTMLResponse)
async def start(
    request: Request, input: DownloadRequest, background_tasks: BackgroundTasks
):
    download = await create_and_begin_download(str(input.url), background_tasks)
    return templates.TemplateResponse(
        "start.html.j2", {"request": request, "download": download}
    )


@router.get("/progress/{request_id}", response_class=HTMLResponse)
async def progress(request: Request, request_id: uuid.UUID):
    # TODO - this is slow, probably deadlocking
    async with get_session() as session:
        download = await get_download_request_or_404(session, request_id)

    headers = {"HX-Trigger": "done"} if download.progress == 100 else {}
    return templates.TemplateResponse(
        "progress.html.j2", {"request": request, "download": download}, headers=headers
    )


@router.get("/download/{request_id}", response_class=Response)
async def download(request_id: uuid.UUID):
    return Response(headers={"HX-Redirect": f"/api/{request_id}"})
