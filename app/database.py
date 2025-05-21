from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

# Load environment variables from .env file
password = os.getenv('DB_PASSWORD')
name = os.getenv('DB_NAME')
host = os.getenv('DB_HOST')
username = os.getenv('DB_USER')

print(f"Connecting to database {name} at {host} with user {username} and password {password}")

# SQLALCHEMY_DATABASE_URL = f'postgresql://{username}:{password}@localhost/{name}'
SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:1308@localhost/tasktracker_db'
engine  = create_engine(SQLALCHEMY_DATABASE_URL)

sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionmaker()
    try:
        yield db
    finally:
        db.close()