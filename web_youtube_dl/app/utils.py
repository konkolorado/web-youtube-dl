import os
import typing
from pathlib import Path

from fastapi.responses import FileResponse, Response
from starlette.datastructures import Headers
from starlette.staticfiles import NotModifiedResponse, StaticFiles
from starlette.types import Scope


class MediaStaticFiles(StaticFiles):
    def file_response(
        self,
        full_path: typing.Union[str, "os.PathLike[str]"],
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
