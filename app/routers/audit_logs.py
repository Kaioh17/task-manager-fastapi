from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
from datetime import datetime, timedelta
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import Optional
from fastapi import File, UploadFile,Form
from .celery_task import delete_row,add_rows
from app.services.audit_logs_service import approve_task_service


router = APIRouter(
    prefix = "/audit-log",
    tags=["Audit-log"]
)

##Admin approval
@router.patch("/approve/{assigned_id}", status_code=status.HTTP_201_CREATED)
async def approve_task(assigned_id: int,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    approve_task_service(assigned_id, db, current_user, add_rows, delete_row,logger)
    return({"msg": f"Task approved by {current_user.user_id}"})