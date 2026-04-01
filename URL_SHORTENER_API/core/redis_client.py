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

class SafeRedis:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host="127.0.0.1",
                port=6379,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1
            )
        except Exception:
            self.client = None

    async def get(self, *args, **kwargs):
        try:
            return await self.client.get(*args, **kwargs)
        except Exception:
            return None

    async def set(self, *args, **kwargs):
        try:
            return await self.client.set(*args, **kwargs)
        except Exception:
            return None

    async def incr(self, *args, **kwargs):
        try:
            return await self.client.incr(*args, **kwargs)
        except Exception:
            return 0

    async def expire(self, *args, **kwargs):
        try:
            return await self.client.expire(*args, **kwargs)
        except Exception:
            return None

redis_client = SafeRedis()