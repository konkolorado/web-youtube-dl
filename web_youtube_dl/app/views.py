import asyncio
import logging

import websockets
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from web_youtube_dl.app.utils import app_root_path
from web_youtube_dl.app.websocket_manager import ConnectionManager
from web_youtube_dl.app.youtube_dl_helpers import QUEUE_SENTINAL

router = APIRouter()
manager = ConnectionManager()

logger = logging.getLogger("web-youtube-dl")

templates_dir = app_root_path / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/favicon.ico")
async def favicon():
    return FileResponse(f"{app_root_path}/static/favicon.ico")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    subscribed, song_title = await manager.subscribe(websocket)
    if not subscribed:
        await websocket.close()
        return

    q = manager.progress_queues[song_title]
    while True:
        value = await q.async_q.get()
        if value == QUEUE_SENTINAL:
            q.async_q.task_done()
            break

        try:
            await manager.broadcast(song_title, value)
        except (
            websockets.exceptions.ConnectionClosedError,
            websockets.exceptions.ConnectionClosedOK,
        ):
            logger.info("Client disconnected during transmission")
            break
        else:
            q.async_q.task_done()

    await manager.unsubscribe(song_title)

    logger.info(
        f"WebSocketManager is tracking {len(manager.progress_queues)} download queues"
    )
    logger.info(f"WebSocketManager is tracking {manager.subscribers} subscribers")
