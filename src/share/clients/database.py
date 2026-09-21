from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings as st

engine: AsyncEngine = create_async_engine(st.database_url, poolclass=NullPool)


async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
