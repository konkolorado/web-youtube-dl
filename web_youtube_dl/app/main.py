import logging
import threading

import janus
import websockets
from fastapi import FastAPI, WebSocket
from uvicorn.logging import DefaultFormatter

import web_youtube_dl
from web_youtube_dl.app import api, views
from web_youtube_dl.app.utils import ConnectionManager, download_file, queues

logger = logging.getLogger("web-youtube-dl")

app = FastAPI()
app.include_router(api.router)
app.include_router(views.router)
manager = ConnectionManager()


@app.on_event("startup")
async def setup_logging():
    handler = logging.StreamHandler()
    formatter = DefaultFormatter("%(levelprefix)s %(asctime)s %(module)s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    song_title = await manager.receive_and_subscribe(websocket)
    logger.info(f"Client subscribed to {song_title}")

    if song_title not in queues:
        queues[song_title] = janus.Queue()
    q = queues[song_title]

    try:
        while True:
            value = await q.async_q.get()
            await manager.broadcast(song_title, value)
            q.async_q.task_done()
    except (
        websockets.exceptions.ConnectionClosedError,
        websockets.exceptions.ConnectionClosedOK,
    ):
        logger.info(f"Client disconnected")
        manager.unsubscribe(song_title, websocket)
        websocket.close()


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    download_file(url)
