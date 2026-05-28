from supabase import create_client, Client
from app.config import settings
from loguru import logger
from typing import Optional, Dict, Any
import time
from datetime import datetime, timedelta


class SimpleCache:
    """Simple in-memory cache (replaces Redis for prototyping)"""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
    
    async def get(self, key: str) -> Optional[str]:
        self._cleanup()
        return self._data.get(key)
    
    async def setex(self, key: str, seconds: int, value: str):
        self._data[key] = value
        self._expiry[key] = time.time() + seconds
    
    async def incr(self, key: str):
        val = int(self._data.get(key, 0))
        self._data[key] = str(val + 1)
        return val + 1
    
    async def expire(self, key: str, seconds: int):
        self._expiry[key] = time.time() + seconds
    
    async def delete(self, key: str):
        self._data.pop(key, None)
        self._expiry.pop(key, None)
    
    async def ping(self):
        return True
    
    def _cleanup(self):
        now = time.time()
        for key, exp in list(self._expiry.items()):
            if exp < now:
                self._data.pop(key, None)
                self._expiry.pop(key, None)


def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


supabase: Client = get_supabase()
cache = SimpleCache()


async def get_cache():
    return cache


async def init_cache():
    logger.info("Using in-memory cache (Redis not required)")


async def close_cache():
    logger.info("Cache closed")

class MockRedis:
    async def get(self, key):
        return None

    async def set(self, key, value):
        return True

    async def delete(self, key):
        return True

redis_client = MockRedis()