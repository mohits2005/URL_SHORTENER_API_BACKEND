from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import os
import urllib.parse
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
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Autheticate": "Bearer"})
    token = auth.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token)

@router.get("google/login")
def google_login():
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": "http://127.0.0.1:8000/auth/google/callback",
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
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://127.0.0.1:8000/auth/google/callback"
        }
    )

    token_data = token_res.json()
    access_token = token_data["access_token"]


    user_info = requests.get(
    "https://www.googleapis.com/oauth2/v3/userinfo",
    headers={"Authorization": f"Bearer {access_token}"},).json()

    email = user_info["email"]

    user = get_user_by_email(db, email)

    if not user:
        user = User(email=email, hashed_password="")
        db.add(user)
        db.commit(user)
        db.refresh(user)

    jwt_token = create_access_token({"sub": user.id})

    return{
        "access_token": jwt_token,
        "token_type": "bearer"
    }
