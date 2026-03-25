from fastapi import HTTPException
from URL_SHORTENER_API.core.redis_client import redis_client


async def rate_limit(identifier: str, limit: int = 5, window: int = 60):

    key = f"rate_limit:{identifier}"

    current = await redis_client.incr(key)

    if current == 1:
        await redis_client.expire(key, window)

    if current > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later."
        )
    
async def get_rate_limit_status(identifier: str, limit: int = 10):

    key = f"rate_limit:{identifier}"

    count = await redis_client.get(key)
    count = int(count) if count else 0

    return {
        "used": count,
        "remaining": max(0, limit - count)
    }