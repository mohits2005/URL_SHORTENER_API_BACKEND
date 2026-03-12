from fastapi import FastAPI
from .database import engine
from . import models
from .routers import authh as auth_router
from .routers import url as urls_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL shortener + auth API")

app.include_router(auth_router.router)
app.include_router(urls_router.router)


@app.get("/")
def root():
    return {"message": "URL Shortener + Auth API", "docs": "/docs", "redoc": "/redoc"}