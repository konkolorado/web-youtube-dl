from typing import Any, Tuple

import janus
import youtube_dl
from fastapi import WebSocket

from web_youtube_dl.app.utils import (
    dl_cache,
    extract_video_title,
    filename_for_url,
    queues,
)


class ConnectionManager:
    def __init__(self):
        self.subscribers = 0
        self.subscriptions: Dict[str, List[WebSocket]] = {}
        self.progress_queues = queues

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def subscribe(self, websocket: WebSocket) -> Tuple[bool, str]:
        download_url = await websocket.receive_text()

        if dl_cache.get((download_url,), None) is not None:
            # If the URL results in a cache hit, the file will not be
            # re-downloaded. So there's no need to subscribe to monitor
            # download progress
            return False, ""

        try:
            filename = filename_for_url(download_url)
        except youtube_dl.utils.DownloadError:
            # If the URL is not something youtube-dl can download,
            # there's no need to subscribe to monitor download progress
            return False, ""

        song_title = extract_video_title(filename=filename)
        if song_title not in self.subscriptions:
            self.subscriptions[song_title] = []
        self.subscriptions[song_title].append(websocket)

        if song_title not in self.progress_queues:
            self.progress_queues[song_title] = janus.Queue()

        self.subscribers += 1
        return True, song_title

    async def unsubscribe(self, song_title: str):
        self.remove_queue(song_title)
        subscribers = self.subscriptions.pop(song_title, [])
        for websocket in subscribers:
            await websocket.close()
            self.subscribers -= 1

    async def broadcast(self, song_title: str, message: str):
        connections = self.subscriptions[song_title]
        for c in connections:
            await c.send_text(f"{message}")

    def remove_queue(self, song_title: str):
        self.progress_queues.pop(song_title, None)