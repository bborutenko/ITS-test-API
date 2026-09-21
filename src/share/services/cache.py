from __future__ import annotations

import redis.asyncio as redis
from fastapi import Depends

from ..clients.cache import get_cache


class CacheService:
    client: redis.Redis

    @classmethod
    def get_service(
        cls, cache_client: redis.Redis = Depends(get_cache)
    ) -> "CacheService":
        service = cls()
        service.client = cache_client
        return service

    async def get(self, *, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, *, key: str, value: str, ex: int | None = None) -> bool:
        return bool(await self.client.set(name=key, value=value, ex=ex))

    async def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        return await self.client.delete(*keys)
