from __future__ import annotations

import logging
from functools import cache, cached_property
from pathlib import Path

import ffmpeg
from pytube import Stream, YouTube
from pytube.helpers import safe_filename

from web_youtube_dl.config import get_download_path

from .progress import ProgressQueues

logger = logging.getLogger(__name__)


class YTDownload:
    def __init__(self, url: str, qs: ProgressQueues | None = None) -> None:
        self.url = url
        self.qs = qs
        logger.debug(f"Created new YTDownload for {url=}")

    @cached_property
    def filename(self) -> str:
        yt = self.yt
        f = safe_filename(yt.title) + ".mp3"
        logger.debug(f"Created filename for {self.url} is {f}")
        return f

    @cached_property
    def yt(self) -> YouTube:
        return YouTube(self.url)

    @cached_property
    def stream(self) -> Stream:
        yt = self.yt
        if self.qs:
            yt.register_on_complete_callback(self._show_complete)
            yt.register_on_progress_callback(self._show_progress)
            logger.debug("Registered progress and completion callbacks")
        return yt.streams.filter(only_audio=True).first()

    def _show_progress(self, s: Stream, _: bytes, remaining_b: int):
        logger.debug(f"Progress callback called for {self.url}: {remaining_b=}")
        percentage_complete = remaining_b / s.filesize
        self.qs.put(s.default_filename, percentage_complete)  # type: ignore

    def _show_complete(self, s: Stream, filepath: str):
        logger.debug(f"Complete callback called for {self.url}: {filepath=}")
        self.qs.terminate(self.filename)  # type: ignore


class DownloadManager:
    def download(self, ytd: YTDownload) -> Path:
        stream = ytd.stream
        download_filename = stream.download(
            output_path=get_download_path(),
            filename=ytd.filename,
            skip_existing=True,
        )
        if self.is_new_download(ytd):
            self._convert_to_mp3(download_filename)
        return Path(download_filename)

    def is_new_download(self, ytd: YTDownload) -> bool:
        dl_path = get_download_path() / Path(ytd.filename)
        return not dl_path.exists()

    @cache
    def _convert_to_mp3(self, filename: str) -> Path:
        original_file = Path(filename)
        new_file = original_file.with_suffix(".tmp")
        stream = ffmpeg.input(original_file.absolute())
        stream = ffmpeg.output(
            stream, filename=str(new_file.absolute()), format="mp3"
        ).r
        ffmpeg.run(stream, overwrite_output=True)
        new_file = new_file.rename(original_file)
        return new_file


if __name__ == "__main__":
    s = "http://youtube.com/watch?v=2lAe1cqCOXo"
    # download(s)
