import logging

from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from web_youtube_dl.config import get_static_path, get_templates_path
from web_youtube_dl.services import progress, websockets

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=get_templates_path())
queues = progress.ProgressQueues()
wm = websockets.WebsocketsManager(queues)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/favicon.ico")
async def favicon():
    return FileResponse(f"{get_static_path()}/favicon.ico")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        filename = await wm.subscribe(websocket)
    except ValueError:
        logger.warning("Unable to subscribe websocket", exc_info=True)
    else:
        await wm.broadcast_until_complete(filename)
        await wm.unsubscribe(filename)
