from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import os
import urllib.parse
import json
from jose import jwt
import URL_SHORTENER_API.schemas as schemas, URL_SHORTENER_API.crud as crud, URL_SHORTENER_API.auth as auth
from URL_SHORTENER_API.deps import get_db
from fastapi import Depends
import requests
from URL_SHORTENER_API.crud import get_user_by_email
from URL_SHORTENER_API.models import User
from URL_SHORTENER_API.auth import create_access_token
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register", response_model=schemas.UserRead)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Email already Exisits")
    
    user = crud.create_user(db, email=user_in.email, hashed_password=auth.hash_password(user_in.password))
    return user

@router.post("/login", response_model=schemas.Token)
def login_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, user_in.email)
    if not user or not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Autheticate": "Bearer"})
    token = auth.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token)

@router.get("/google/login")
def google_login():
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID").strip(),
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI").strip(),
        "access_type": "offline",
        "prompt": "consent",
    }

    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID").strip(),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET").strip(),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI").strip()
        }
    )
    if token_res.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Google Authentication failed"
        )

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="google didn't return a access token"
        )
    
    user_info = requests.get(
    "https://www.googleapis.com/oauth2/v3/userinfo",
    headers={"Authorization": f"Bearer {access_token}"},)

    if user_info.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail="Failed to retrieve google user profile information"
        )
    user_res = user_info.json()

    email = user_res.get("email")
    if not email:
        raise HTTPException(
            status_code=400,
            detail="User's google account email is not available"
        )
    
    user = get_user_by_email(db, email)

    if not user:
        user = User(email=email, hashed_password="")
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token({"sub": str(user.id)})

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8501")
    redirect_url = f"{frontend_url.rstrip('/')}/?token={jwt_token}"
    return RedirectResponse(url=redirect_url)
    # return{
    #     "access_token": jwt_token,
    #     "token_type": "bearer"
    # }
