from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .models.config import Settings

settings = Settings()

SQLALCHEMY_DATABASE_URL = settings.db_url
engine  = create_engine(SQLALCHEMY_DATABASE_URL)

sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()