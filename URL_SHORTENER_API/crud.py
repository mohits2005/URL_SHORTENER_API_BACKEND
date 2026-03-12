import random
import string
from sqlalchemy.orm import Session
import URL_SHORTENER_API.models as models


def get_user_by_email(db: Session, email: str):

    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str):
    user = models.User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def generate_short_code(length: int = 6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def create_unique_short_code(db: Session, length: int = 6):
    while True:
        code = generate_short_code(length)
        existing = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not existing:
            return code
        
def create_url(db: Session, owner_id: int, target_url: str, short_code: str):
    url = models.URL(short_code=short_code, target_url=target_url, owner_id=owner_id)
    db.add(url)
    db.commit()
    db.refresh(url)
    return url

def get_url_by_shortcode(db: Session, short_code: str):
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()

def list_user_urls(db: Session, owner_id):
    return db.query(models.URL).filter(models.URL.owner_id == owner_id).all()