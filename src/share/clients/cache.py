from typing import AsyncIterator

import redis.asyncio as redis

from config.settings import settings as st


async def get_cache() -> AsyncIterator[redis.Redis]:
    client: redis.Redis = redis.from_url(
        st.CACHE_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()
