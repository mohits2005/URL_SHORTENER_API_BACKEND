from URL_SHORTENER_API.database import sessionLocal

def get_db():

    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
        