from fastapi import FastAPI
from .models import db_models
from .database import engine
from .routers import org, user, task,auth, assign_tasks

db_models.Base.metadata.create_all(bind=engine)
app = FastAPI()

"""routers"""
app.include_router(org.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(auth.router)
app.include_router(assign_tasks.router)




