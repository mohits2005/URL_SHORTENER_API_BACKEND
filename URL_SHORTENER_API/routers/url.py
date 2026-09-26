from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from URL_SHORTENER_API.services.url_service import get_original_url, increment_clicks
from fastapi import Request
from URL_SHORTENER_API.services.rate_limiter import rate_limit
import asyncio
from URL_SHORTENER_API.core.redis_client import redis_client
import URL_SHORTENER_API.schemas as schemas, URL_SHORTENER_API.crud as crud, URL_SHORTENER_API.auth as auth  
from URL_SHORTENER_API.deps import get_db
import URL_SHORTENER_API.models as models

router = APIRouter(tags=["urls"])

@router.post("/urls", response_model=schemas.URLRead)
def create_url(url_in: schemas.URLCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    target_url = str(url_in.target_url)
    existing_url = (db.query(models.URL).filter(models.URL.target_url == target_url,
                                                models.URL.owner_id == current_user.id).first()
                   )
    if existing_url:
        return existing_url
    short_code = crud.create_unique_short_code(db, owner_id=current_user.id, target_url=str(url_in.target_url), user_id=current_user.id)
    url = crud.create_url(db, owner_id=current_user.id, target_url=str(url_in.target_url), short_code=short_code)
    return url

@router.get("/urls", response_model=List[schemas.URLRead])
def get_list_urls(current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.list_user_urls(db, current_user.id)

@router.get("/u/{short_code}")
async def redirect_short_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    client_ip = request.client.host
    await rate_limit(client_ip, limit=10, window=60)

    url = await get_original_url(short_code, db)

    if not url:
        raise HTTPException(status_code=404, detail="short URL not found")

    background_tasks.add_task(increment_clicks, short_code)

    return RedirectResponse(url=url, status_code=307)
