import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import janus
import youtube_dl
from cachetools import Cache, cached
from fastapi import WebSocket

import web_youtube_dl

logger = logging.getLogger("web-youtube-dl")
queues: Dict[str, janus.Queue] = {}
QUEUE_SENTINAL = None
dl_cache = Cache(maxsize=1000)


def app_root_path():
    return Path(__file__).absolute().parent


def module_root_path():
    return Path(web_youtube_dl.__file__).absolute().parent


def download_path() -> str:
    output_path = os.environ.get("YT_DOWNLOAD_PATH")
    if output_path is None:
        output_path = f"{module_root_path()}/downloads/"
    return output_path


@cached(dl_cache)
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

        try:
            queues[song_title].sync_q.put(downloaded_percent)
        except KeyError:
            # It's possible that when the thread starts running, the
            # websocket connection hasnt yet created a queues entry for
            # the song_title in question. Just pass and maybe for the next
            # download status it'll have been created
            logger.error(
                f"Unable to retrieve queue for {song_title} to send {downloaded_percent}"
            )

    if resp["status"] == "finished":
        song_title = extract_video_title(filename=resp["filename"])
        try:
            queues[song_title].sync_q.put(QUEUE_SENTINAL)
        except KeyError:
            logger.error(
                f"Unable to retrieve queue for {song_title} to send {QUEUE_SENTINAL}"
            )


def filename_for_url(url: str) -> str:
    ydl_opts = download_opts()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result: List[Dict] = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(result)
        filename = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return Path(filename).name


def extract_video_title(*, filename: str) -> str:
    return Path(filename).stem


def cli_download():
    import sys

    url = sys.argv[1]
    download_file(url)
