from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from ..core import oauth2
from ..services import task_service
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(
    prefix = "/task",
    tags = ['Tasks']
)

#only user_role with admin can use the app feature
@router.post("/create" , status_code = status.HTTP_201_CREATED, response_model=schemas.TaskOut)
def create_task(task: schemas.TaskBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    logger.info(f"User {current_user.user_id} attempting to create a task.")
    role  =  current_user.user_role
    if role.lower() == "user":
        logger.warning(f"Access denied for user {current_user.user_id} with role {role}.")
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                            detail = "Access denied: insufficient role")
    task_query = task_service.create_task_service(current_user, task, db)

    logger.info(f"Task created with task_id={task_query.task_id} by user {current_user.user_id}.")
    return task_query

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.TaskOut])
def tasks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    logger.info(f"Fetching tasks for org_id={current_user.org_id} by user {current_user.user_id}.")
    task = task_service.get_task_service(db, current_user)
    logger.info(f"Fetched {len(task)} tasks for org_id={current_user.org_id}.")
    return task