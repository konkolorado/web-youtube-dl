import logging

import uvicorn
from fastapi import FastAPI
from uvicorn.logging import DefaultFormatter

from web_youtube_dl.app import api, views
from web_youtube_dl.app.utils import download_file

logger = logging.getLogger("web-youtube-dl")

app = FastAPI()
app.include_router(api.router)
app.include_router(views.router)


@app.on_event("startup")
async def setup_logging():
    handler = logging.StreamHandler()
    formatter = DefaultFormatter("%(levelprefix)s %(asctime)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="debug", reload=True)
