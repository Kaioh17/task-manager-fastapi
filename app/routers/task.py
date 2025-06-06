from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from ..core import oauth2
import logging

router = APIRouter(
    prefix = "/task",
    tags = ['Tasks']
)

#only user_role with admin can use the app feature
@router.post("/" , status_code = status.HTTP_201_CREATED, response_model=schemas.TaskOut)
def create_task(task: schemas.TaskBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    logging.info(f"User {current_user.user_id} attempting to create a task.")
    role  =  current_user.user_role
    if role.lower() != "admin":
        logging.warning(f"Access denied for user {current_user.user_id} with role {role}.")
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "Access denied: insufficient role")
    task_query = db_models.Tasks(org_id = current_user.org_id, **task.dict())
    db.add(task_query)
    db.commit()
    db.refresh(task_query)
    logging.info(f"Task created with task_id={task_query.task_id} by user {current_user.user_id}.")
    return task_query

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.TaskOut])
def tasks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    logging.info(f"Fetching tasks for org_id={current_user.org_id} by user {current_user.user_id}.")
    task = db.query(db_models.Tasks).filter(db_models.Tasks.org_id == current_user.org_id).all()
    logging.info(f"Fetched {len(task)} tasks for org_id={current_user.org_id}.")
    return task