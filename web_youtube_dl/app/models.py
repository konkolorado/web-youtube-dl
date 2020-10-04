from pydantic import BaseModel


class DownloadRequest(BaseModel):
    url: str


class DownloadResponse(BaseModel):
    filename: str
