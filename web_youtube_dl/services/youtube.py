from __future__ import annotations

import logging
import tempfile
import typing as t
import uuid
from functools import cached_property, partial
from pathlib import Path

import ffmpeg
from anyio import to_thread
from anyio.from_thread import start_blocking_portal
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


class DownloadManager:
    def __init__(self, ytd: YTDownload):
        self.ytd = ytd
        on_progress_callback = partial(self.sync_callback, self._progress_callback)
        self.ytd.yt.register_on_progress_callback(on_progress_callback)
        on_complete_callback = partial(self.sync_callback, self._completion_callback)
        self.ytd.yt.register_on_complete_callback(on_complete_callback)

    def sync_callback(self, callback, *args, **kwargs):
        with start_blocking_portal() as portal:
            portal.call(callback, *args, **kwargs)

    async def _progress_callback(self, s: Stream, _: bytes, remaining_b: int):
        percentage_complete = int(remaining_b / s.filesize * 100)
        async with get_session() as session:
            requests = RequestRepo(session)
            await requests.update_downloading_request(
                self.ytd.req_id, percentage_complete
            )

    async def _completion_callback(self, _: t.Any, filepath: str | None):
        async with get_session() as session:
            requests = RequestRepo(session)
            await requests.complete_downloading_request(self.ytd.req_id)

    async def download_and_process(self, mm: MetadataManager, db: RequestRepo):
        with tempfile.NamedTemporaryFile() as fp:
            filepath = await to_thread.run_sync(self.download, fp.name)
            await to_thread.run_sync(self.convert_to_mp3, filepath)
            await to_thread.run_sync(self.apply_metadata, mm, filepath)
            await self.store_to_db(db, filepath)

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

    async def store_to_db(self, db: RequestRepo, filepath: Path):
        with filepath.open("rb") as f:
            data = f.read()

        if (request := await db.get_request(self.ytd.req_id)) is None:
            return
        await db.complete_request(request, data)
