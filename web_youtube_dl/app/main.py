import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from web_youtube_dl.app import api, views
from web_youtube_dl.config import get_app_port, init_logging
from web_youtube_dl.db import create_db
from web_youtube_dl.services import metadata, youtube


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logging()
    await create_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api.router, prefix="/api")
app.include_router(views.router)


def run_app():
    uvicorn.run(
        "web_youtube_dl.app.main:app",
        host="0.0.0.0",
        port=get_app_port(),
        log_level="debug",
        reload=True,
    )


async def _cli_download():
    # TODO: run API in a thread and call it
    import os
    import sys
    import uuid

    if "YT_DOWNLOAD_PATH" not in os.environ:
        os.environ["YT_DOWNLOAD_PATH"] = "."
    url = sys.argv[1]
    ytd = youtube.YTDownload(url=url, request_id=uuid.uuid4())
    dlm = youtube.DownloadManager(ytd)
    mm = metadata.MetadataManager()
    await dlm.download_and_process(mm)


def cli_download():
    asyncio.run(_cli_download())


if __name__ == "__main__":
    uvicorn.run(
        "web_youtube_dl.app.main:app",
        host="127.0.0.1",
        port=get_app_port(),
        log_level="debug",
        reload=True,
    )
