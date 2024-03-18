from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from web_youtube_dl.app import api, views
from web_youtube_dl.config import get_app_port, init_logging
from web_youtube_dl.db import create_db


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
