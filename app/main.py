from fastapi import FastAPI
from .models import db_models
from .database import engine
from .routers import audit_logs, org, user, task,auth, assign_tasks
import logging

logging.basicConfig(
    level=logging.INFO,
     format="%(asctime)s %(levelname)s - %(message)s"
)

db_models.Base.metadata.create_all(bind=engine)
app = FastAPI()
##adding the limiter to the router
app.state.limiter = auth.limiter
"""routers"""
app.include_router(org.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(auth.router)
app.include_router(assign_tasks.router)
app.include_router(audit_logs.router)





