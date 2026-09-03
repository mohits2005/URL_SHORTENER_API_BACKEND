# import redis.asyncio as redis

# try:
#     redis_client = redis.Redis(
#         host="127.0.0.1",
#         port=6379,
#         decode_responses=True
#     )
# except Exception:
#     redis_client = None

import redis.asyncio as redis
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from upstash_redis.asyncio import Redis



class SafeRedis:
    def __init__(self):
        self.client = None

        try:
            redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
            redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

            if not redis_url or not redis_token:
                raise ValueError("REDIS_URL, REDIS_TOKEN is not configured")

            self.client = Redis(
                redis_url,
                redis_token
            )

        except Exception:
            self.client = None

    async def get(self, *args, **kwargs):
        if not self.client:
            return None

        try:
            return await self.client.get(*args, **kwargs)
        except Exception:
            return None

    async def set(self, *args, **kwargs):
        if not self.client:
            return None

        try:
            return await self.client.set(*args, **kwargs)
        except Exception:
            return None

    async def incr(self, *args, **kwargs):
        if not self.client:
            return 0

        try:
            return await self.client.incr(*args, **kwargs)
        except Exception:
            return 0

    async def expire(self, *args, **kwargs):
        if not self.client:
            return None

        try:
            return await self.client.expire(*args, **kwargs)
        except Exception:
            return None


redis_client = SafeRedis()
# async def test():
#     await redis_client.set("safe_test", "hello")

#     value = await redis_client.get("safe_test")

#     print("Value:", value)


# asyncio.run(test())
