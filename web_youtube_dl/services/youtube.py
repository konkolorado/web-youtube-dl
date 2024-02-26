from __future__ import annotations

import logging
import tempfile
import uuid
from functools import cached_property
from pathlib import Path

import ffmpeg
from pytube import Stream, YouTube

from web_youtube_dl.config import get_download_path
from web_youtube_dl.db import RequestRepo, get_session

from .metadata import MetadataManager

logger = logging.getLogger(__name__)


class YTDownload:
    def __init__(self, url: str, request_id: uuid.UUID) -> None:
        self.url = url
        self.req_id = request_id
        self.yt = YouTube(self.url)
        self.title = self.yt.title

    @cached_property
    def stream(self) -> Stream:
        if (stream := self.yt.streams.filter(only_audio=True).first()) is None:
            raise Exception("Unable to find stream")
        return stream

    def _show_progress(self, s: Stream, _: bytes, remaining_b: int):
        # TODO: use this to update the DB
        logger.debug(f"Progress callback called for {self.url}: {remaining_b=}")
        percentage_complete = remaining_b / s.filesize
        self.pqs.put(s.default_filename, percentage_complete)  # type: ignore

    def _show_complete(self, s: Stream, filepath: str):
        logger.debug(f"Complete callback called for {self.url}: {filepath=}")
        self.pqs.terminate(self.filename)  # type: ignore


class DownloadManager:
    def __init__(self, ytd: YTDownload):
        self.ytd = ytd

    async def download_and_process(self, mm: MetadataManager):
        # TODO: make this thing async
        with tempfile.NamedTemporaryFile() as fp:
            filepath = self.download(fp.name)
            self.convert_to_mp3(filepath)
            self.apply_metadata(mm, filepath)
            await self.store_to_db(filepath)

    def download(self, filename: str) -> Path:
        stream = self.ytd.stream
        download_filename = stream.download(
            output_path=get_download_path(), filename=filename, skip_existing=True
        )
        logger.info(f"Downloaded {self.ytd.url} to {download_filename}")
        return Path(download_filename)

    def convert_to_mp3(self, filepath: Path) -> Path:
        new_file = filepath.with_suffix(".tmp")
        stream = ffmpeg.input(filepath.absolute())
        stream = ffmpeg.output(
            stream, filename=str(new_file.absolute()), format="mp3", vn=None
        )
        ffmpeg.run(stream, overwrite_output=True)
        new_file.rename(filepath)
        logger.info(f"Converted {str(filepath)} to mp3")
        return filepath

    def apply_metadata(self, mm: MetadataManager, filepath: Path):
        title = self.ytd.title
        if metadata := mm.search(title):
            mm.apply_metadata(metadata, str(filepath))
            logger.info(f"Applied metadata to {str(filepath)}")

    async def store_to_db(self, filepath: Path):
        with filepath.open("rb") as f:
            data = f.read()

        async with get_session() as session:
            rrepo = RequestRepo(session)
            if (request := await rrepo.get_request(self.ytd.req_id)) is None:
                return
            await rrepo.complete_request(request, data)
