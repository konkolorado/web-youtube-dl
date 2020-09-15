import functools
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import janus
import youtube_dl
from fastapi import WebSocket

import web_youtube_dl

logger = logging.getLogger("web-youtube-dl")
queues: Dict[str, janus.Queue] = {}


def app_root_path():
    return Path(__file__).absolute().parent


def module_root_path():
    return Path(web_youtube_dl.__file__).absolute().parent


def download_path() -> str:
    output_path = os.environ.get("YT_DOWNLOAD_PATH")
    if output_path is None:
        output_path = f"{module_root_path()}/downloads/"
    return output_path


@functools.lru_cache(maxsize=None)
def download_file(url: str) -> str:
    ydl_opts = download_opts()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.extract_info(url, download=True)
        except (youtube_dl.utils.DownloadError, FileNotFoundError) as e:
            logger.exception(f"Error downloading file: {e}", exc_info=False)

        return filename_for_url(url)


def download_opts() -> Dict[str, Any]:
    return {
        "format": "bestaudio/best",
        "logger": logger,
        "noplaylist": True,
        "outtmpl": f"{download_path()}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "progress_hooks": [_download_status_hook],
        "noprogress": True,
    }


def _download_status_hook(resp: Dict[str, Any]):
    if resp["status"] == "downloading":
        song_title = extract_video_title(filename=resp["filename"])
        downloaded_percent = (resp["downloaded_bytes"] * 100) / resp["total_bytes"]
        downloaded_percent = round(downloaded_percent)
        queues[song_title].sync_q.put(downloaded_percent)


def filename_for_url(url: str) -> str:
    ydl_opts = download_opts()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result: List[Dict] = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(result)
        filename = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return Path(filename).name


def extract_video_title(*, filename: str) -> str:
    return Path(filename).stem


class ConnectionManager:
    def __init__(self):
        self.subscriptions: Dict[str, List[WebSocket]] = {}

    async def receive_and_subscribe(self, websocket: WebSocket):
        download_url = await websocket.receive_text()
        filename = filename_for_url(download_url)
        song_title = extract_video_title(filename=filename)

        self.subscribe(song_title, websocket)
        return song_title

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    def unsubscribe(self, channel: str, websocket: WebSocket):
        self.subscriptions[channel].remove(websocket)

    async def broadcast(self, channel: str, message: str):
        connections = self.subscriptions[channel]
        for c in connections:
            await c.send_text(f"{message}")

    def subscribe(self, channel: str, websocket: WebSocket):
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []
        self.subscriptions[channel].append(websocket)
