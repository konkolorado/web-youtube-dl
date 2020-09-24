import logging

import uvicorn
from fastapi import FastAPI
from uvicorn.logging import DefaultFormatter
from web_youtube_dl.app import api, views
from web_youtube_dl.app.utils import MediaStaticFiles, app_port, download_path

logger = logging.getLogger("web-youtube-dl")

app = FastAPI()
app.include_router(api.router)
app.include_router(views.router)

app.mount("/download", MediaStaticFiles(directory=download_path()), name="downloads")


@app.on_event("startup")
async def setup_logging():
    handler = logging.StreamHandler()
    formatter = DefaultFormatter("%(levelprefix)s %(asctime)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


def run_app():
    uvicorn.run(
        "web_youtube_dl.app.main:app",
        host="0.0.0.0",
        port=app_port(),
        log_level="debug",
        reload=False,
    )


if __name__ == "__main__":
    uvicorn.run(
        "web_youtube_dl.app.main:app",
        host="127.0.0.1",
        port=app_port(),
        log_level="debug",
        reload=True,
    )
