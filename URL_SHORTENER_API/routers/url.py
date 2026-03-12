from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session


import URL_SHORTENER_API.schemas as schemas, URL_SHORTENER_API.crud as crud, URL_SHORTENER_API.auth as auth  
from URL_SHORTENER_API.deps import get_db

router = APIRouter(tags=["urls"])

@router.post("/urls", response_model=schemas.URLRead)
def create_url(url_in: schemas.URLCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    short_code = crud.create_unique_short_code(db)
    url = crud.create_url(db, owner_id=current_user.id, target_url=str(url_in.target_url), short_code=short_code)
    return url

@router.get("/urls", response_model=List[schemas.URLRead])
def get_list_urls(current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return crud.list_user_urls(db, current_user.id)

@router.get("/u/{short_code}")
def redirect_short_url(short_code: str, db: Session = Depends(get_db)):
    url_obj = crud.get_url_by_shortcode(db, short_code)
    if not url_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="short URL not found")
    url_obj.clicks += 1
    db.commit()
    return RedirectResponse(url=url_obj.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
