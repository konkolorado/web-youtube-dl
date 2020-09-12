import logging
import threading

import websockets
from fastapi import FastAPI, WebSocket
from uvicorn.logging import DefaultFormatter

import web_youtube_dl
from web_youtube_dl.app import api, views
from web_youtube_dl.app.utils import download_file, download_path, progress_queue

logger = logging.getLogger("web-youtube-dl")

app = FastAPI()
app.include_router(api.router)
app.include_router(views.router)


@app.on_event("startup")
async def setup_logging():
    handler = logging.StreamHandler()
    formatter = DefaultFormatter("%(levelprefix)s %(asctime)s %(module)s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            print(f"In websocket: {threading.currentThread()}")
            value = await progress_queue.async_q.get()
            print("Got from queue:", value)
            await websocket.send_text(f"{value}")
    except websockets.exceptions.ConnectionClosedError:
        print("Client left ws connection")

        websocket.close()


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    download_file(url)
