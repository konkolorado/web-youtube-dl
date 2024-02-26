from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSession_

logger = logging.getLogger(__name__)


DATABASE_URL = "sqlite+aiosqlite:///music.db"
# engine = create_async_engine(DATABASE_URL, echo=True)
engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(engine, class_=AsyncSession_, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def get_session() -> AsyncSession_:
    return async_session()
