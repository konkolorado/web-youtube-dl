import os
import typing
from pathlib import Path

import web_youtube_dl
from fastapi.responses import FileResponse, Response
from starlette.datastructures import Headers
from starlette.staticfiles import NotModifiedResponse, StaticFiles
from starlette.types import Scope

app_root_path = Path(__file__).absolute().parent
module_root_path = Path(web_youtube_dl.__file__).absolute().parent


def filename_to_song_title(filename: str) -> str:
    return Path(filename).with_suffix(".mp3").name


def download_path() -> str:
    output_path = os.environ.get("YT_DOWNLOAD_PATH")
    if output_path is None:
        output_path = f"{module_root_path}/downloads/"
    Path(output_path).mkdir(parents=True, exist_ok=True)
    return output_path


def app_port() -> int:
    port: str = os.environ.get("YT_DOWNLOAD_PORT", "5000")
    try:
        return int(port)
    except ValueError:
        return 5000


PathLike = typing.Union[str, "os.PathLike[str]"]


class MediaStaticFiles(StaticFiles):
    def file_response(
        self,
        full_path: PathLike,
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = 200,
    ) -> Response:
        method = scope["method"]
        request_headers = Headers(scope=scope)
        filename = Path(full_path).name

        response = FileResponse(
            full_path,  # type: ignore
            status_code=status_code,
            stat_result=stat_result,
            method=method,
            media_type="audio/mpeg",
            filename=filename,
        )
        if self.is_not_modified(response.headers, request_headers):
            return NotModifiedResponse(response.headers)
        return response
