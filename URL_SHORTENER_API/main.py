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

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/debug/client_info")
async def get_user_ip(request: Request):
    return {
        "client_host": request.client.host if request.client else None,
        "x_forwarded_for": request.headers.get("x-forwarded-for"),
        "x_real_ip": request.headers.get("x_real_ip"),
        "forwarded": request.headers.get("forwarded"),
        "host": request.headers.get("host"),
    }
