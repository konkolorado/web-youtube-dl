import typing as t
import uuid

import arrow


class DownloadResponse(t.TypedDict):
    id: uuid.UUID
    download_url: str
    status: int
    progress: int
    updated_at: arrow.Arrow
    created_at: arrow.Arrow
    completed_at: arrow.Arrow
