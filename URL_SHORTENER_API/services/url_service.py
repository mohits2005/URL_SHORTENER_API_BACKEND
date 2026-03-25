from sqlalchemy.orm import Session
# from URL_SHORTENER_API.services.url_service import get_original_url, increment_clicks
 
from URL_SHORTENER_API.core.redis_client import redis_client
import redis
import URL_SHORTENER_API.crud as crud
from URL_SHORTENER_API.database import sessionLocal
from URL_SHORTENER_API import models

async def get_original_url(short_code: str, db):

    cached = await redis_client.get(short_code)

    if cached:
        if cached == "NULL":
            return None
        return cached

    url_obj = db.query(models.URL).filter(
        models.URL.short_code == short_code
    ).first()

    if not url_obj:
        await redis_client.set(short_code, "NULL", ex=60)
        return None

    original_url = url_obj.target_url

    await redis_client.set(short_code, original_url, ex=3600)

    return original_url

def increment_clicks(short_code: str):
    db = sessionLocal()
    try:
        url_obj = crud.get_url_by_shortcode(db, short_code)
        if url_obj:
            url_obj.clicks += 1
            db.commit()
    finally:
        db.close()
        