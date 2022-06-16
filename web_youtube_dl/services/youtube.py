from __future__ import annotations

import logging
from functools import cached_property
from pathlib import Path

import ffmpeg
from pytube import Stream, YouTube
from pytube.helpers import safe_filename

from web_youtube_dl.config import get_download_path

from .metadata import MetadataManager
from .progress import ProgressQueues

logger = logging.getLogger(__name__)


class YTDownload:
    def __init__(self, url: str, *, pqs: ProgressQueues | None = None) -> None:
        self.url = url
        self.pqs = pqs

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
        if self.pqs:
            yt.register_on_complete_callback(self._show_complete)
            yt.register_on_progress_callback(self._show_progress)
            logger.debug("Registered progress and completion callbacks")
        return yt.streams.filter(only_audio=True).first()

    def _show_progress(self, s: Stream, _: bytes, remaining_b: int):
        logger.debug(f"Progress callback called for {self.url}: {remaining_b=}")
        percentage_complete = remaining_b / s.filesize
        self.pqs.put(s.default_filename, percentage_complete)  # type: ignore

    def _show_complete(self, s: Stream, filepath: str):
        logger.debug(f"Complete callback called for {self.url}: {filepath=}")
        self.pqs.terminate(self.filename)  # type: ignore


class DownloadManager:
    def _filepath_from_ytd(self, ytd: YTDownload) -> Path:
        return get_download_path() / Path(ytd.filename)

    def is_new_download(self, ytd: YTDownload) -> bool:
        dl_path = self._filepath_from_ytd(ytd)
        return not dl_path.exists()

    def download_and_process(
        self, ytd: YTDownload, mm: MetadataManager, pqs: ProgressQueues | None = None
    ) -> Path:
        if not self.is_new_download(ytd):
            if pqs:
                pqs.terminate(ytd.filename)
            return self._filepath_from_ytd(ytd)
        filepath = self.download(ytd)
        self.convert_to_mp3(filepath)
        self.apply_metadata(mm, filepath)
        return filepath

    def apply_metadata(self, mm: MetadataManager, filepath: Path):
        title = filepath.stem
        if metadata := mm.search(title):
            mm.apply_metadata(metadata, str(filepath))
            logger.info(f"Applied metadata to {str(filepath)}")

    def download(self, ytd: YTDownload) -> Path:
        stream = ytd.stream
        self.is_new_download(ytd)
        download_filename = stream.download(
            output_path=get_download_path(),
            filename=ytd.filename,
            skip_existing=True,
        )
        logger.info(f"Downloaded {ytd.filename} to {download_filename}")
        return Path(download_filename)

    def convert_to_mp3(self, filepath: Path) -> Path:
        new_file = filepath.with_suffix(".tmp")
        stream = ffmpeg.input(filepath.absolute())
        stream = ffmpeg.output(
            stream,
            filename=str(new_file.absolute()),
            format="mp3",
            vn=None,
        )
        ffmpeg.run(stream, overwrite_output=True)
        new_file.rename(filepath)
        logger.info(f"Converted {str(filepath)} to mp3")
        return filepath


if __name__ == "__main__":
    s = "http://youtube.com/watch?v=2lAe1cqCOXo"
    # download(s)
