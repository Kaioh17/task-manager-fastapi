from celery import Celery
from ..models.config import Settings

settings = Settings()

celery_app = Celery(
    "app",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.routers.celery_task"]

)