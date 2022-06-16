import uvicorn
from fastapi import FastAPI

from web_youtube_dl.app import api, views
from web_youtube_dl.app.utils import MediaStaticFiles
from web_youtube_dl.config import get_app_port, get_download_path, init_logging
from web_youtube_dl.services import metadata, youtube

app = FastAPI()
app.include_router(api.router)
app.include_router(views.router)
app.mount(
    "/download", MediaStaticFiles(directory=get_download_path()), name="downloads"
)


@app.on_event("startup")
async def setup_logging():
    init_logging()


def run_app():
    uvicorn.run(
        "web_youtube_dl.app.main:app",
        host="0.0.0.0",
        port=get_app_port(),
        log_level="debug",
        reload=False,
    )


def cli_download():
    import os
    import sys

    if "YT_DOWNLOAD_PATH" not in os.environ:
        os.environ["YT_DOWNLOAD_PATH"] = "."
    url = sys.argv[1]
    ytd = youtube.YTDownload(url)
    dlm = youtube.DownloadManager()
    mm = metadata.MetadataManager()
    dlm.download_and_process(ytd, mm)


if __name__ == "__main__":
    uvicorn.run(
        "web_youtube_dl.app.main:app",
        host="127.0.0.1",
        port=get_app_port(),
        log_level="debug",
        reload=True,
    )
