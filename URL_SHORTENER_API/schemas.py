from typing import List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl

class UserCreate(BaseModel):

    email: EmailStr
    password: str

class UserRead(BaseModel):

    id: int
    email: EmailStr

    class config:
        orm_mode=True

class Token(BaseModel):

    access_token: str
    token_type: str = "bearer"

class URLCreate(BaseModel):

    target_url: HttpUrl

class URLRead(BaseModel):

    id: int
    short_code: str
    target_url: HttpUrl
    clicks: int

    class config:
        orm_mode=True
        