import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Optional


class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        self.redis = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if not self.redis:
            await self.connect()
        
        if ttl is None:
            ttl = settings.redis_cache_ttl
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        await self.redis.setex(key, ttl, value)

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            await self.connect()
        
        value = await self.redis.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def delete(self, key: str):
        if not self.redis:
            await self.connect()
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        if not self.redis:
            await self.connect()
        return await self.redis.exists(key) > 0

    async def clear_pattern(self, pattern: str):
        if not self.redis:
            await self.connect()
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


redis_manager = RedisManager()
