import logging
from pathlib import Path
from typing import Any, Dict, List

import janus
import youtube_dl
from cachetools import Cache, cached
from web_youtube_dl.app.utils import (
    download_path,
    filename_to_song_title,
    module_root_path,
)

logger = logging.getLogger("web-youtube-dl")
dl_cache = Cache(maxsize=1000)
queues: Dict[str, janus.Queue] = {}
QUEUE_SENTINAL = None


@cached(dl_cache)
def download_file(url: str) -> str:
    with youtube_dl.YoutubeDL(ydl_dl_opts) as ydl:
        try:
            ydl.extract_info(url, download=True)
        except (youtube_dl.utils.DownloadError, FileNotFoundError) as e:
            logger.exception(f"Error downloading file: {e}", exc_info=False)

        return url_to_filename(url)


def _download_status_hook(resp: Dict[str, Any]):
    if resp["status"] == "downloading":
        song_title = filename_to_song_title(filename=resp["filename"])
        downloaded_percent = (resp["downloaded_bytes"] * 100) / resp["total_bytes"]
        downloaded_percent = round(downloaded_percent)

        try:
            queues[song_title].sync_q.put(downloaded_percent)
        except KeyError:
            # It's possible that when the thread starts running, the
            # websocket connection hasnt yet created a queues entry for
            # the song_title in question. Just pass and maybe for the next
            # download status it'll have been created
            logger.info(
                f"Unable to retrieve queue for {song_title} to send {downloaded_percent}"
            )

    if resp["status"] == "finished":
        song_title = filename_to_song_title(filename=resp["filename"])
        try:
            queues[song_title].sync_q.put(QUEUE_SENTINAL)
        except KeyError:
            logger.info(
                f"Unable to retrieve queue for {song_title} to send {QUEUE_SENTINAL}"
            )


def url_to_filename(url: str) -> str:
    with youtube_dl.YoutubeDL(ydl_dl_opts) as ydl:
        result: List[Dict] = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(result)
        return Path(filename).with_suffix(".mp3").name


ydl_dl_opts = {
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
    "cachedir": f"{download_path()}/.cache",
}


def cli_download():
    import sys

    url = sys.argv[1]
    download_file(url)
