import logging
from collections import defaultdict

import pytube
import pytube.exceptions
import websockets
import websockets.exceptions
from fastapi import WebSocket

from . import progress, youtube

logger = logging.getLogger(__name__)


class WebsocketsManager:
    def __init__(self, pqs: progress.ProgressQueues) -> None:
        self.queues = pqs
        self.subscriptions: dict[str, list[WebSocket]] = defaultdict(list)

    async def subscribe(self, websocket: WebSocket) -> str:
        await websocket.accept()
        download_url = await websocket.receive_text()
        ytd = youtube.YTDownload(download_url)

        try:
            self.subscriptions[ytd.filename].append(websocket)
        except pytube.exceptions.RegexMatchError as e:
            raise ValueError(f"Invalid url: {download_url}") from e
        return ytd.filename

    async def unsubscribe(self, filename: str):
        subscribers = self.subscriptions.pop(filename, [])
        for websocket in subscribers:
            await websocket.close()

    async def broadcast(self, filename: str, message: str):
        for connection in self.subscriptions[filename]:
            try:
                await connection.send_text(f"{message}")
            except (
                websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.ConnectionClosedOK,
            ):
                logger.info("Client disconnected during broadcast", exc_info=True)

    async def broadcast_until_complete(self, filename: str):
        while True:
            value = await self.queues.get(filename)
            await self.broadcast(filename, str(value))
            if value == self.queues.QUEUE_SENTINAL:
                break
