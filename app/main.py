from fastapi import FastAPI
from .models import db_models
from .database import engine, get_db
from sqlalchemy.orm import Session
from fastapi.params import Depends
from .routers import org, user, task
db_models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(org.router)
app.include_router(user.router)
app.include_router(task.router)

@app.get("/")
def root():
    return {"Welcome to your taskmanager" : "name?"}



