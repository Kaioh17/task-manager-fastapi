from celery import Celery
from ..models.config import Settings

settings = Settings()
# # Create Celery app with proper module name and task discovery
# celery_app = Celery(
#     "app", 
#     broker=f"sqlalchemy+{settings.db_url}",
#     backend=f"db+{settings.db_url}",
#     include=["app.routers.celery_task"]  # Tell Celery where to find tasks
# )

celery_app = Celery(
    "app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.routers.celery_task"]

)