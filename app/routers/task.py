from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from ..core import oauth2

router = APIRouter(
    prefix = "/task",
    tags = ['Tasks']
)

#only user_role with admin can use the app feature
@router.post("/" , status_code = status.HTTP_201_CREATED, response_model=schemas.TaskOut)
def create_task(task: schemas.TaskBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    role  =  current_user.user_role
    if role.lower() != "admin":
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "Access denied: insufficient role")

    task_query = db_models.Tasks(org_id = current_user.org_id, **task.dict())

    db.add(task_query)
    db.commit()
    db.refresh(task_query)

    return task_query

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.TaskOut])
def tasks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    task = db.query(db_models.Tasks).filter(db_models.Tasks.org_id == current_user.org_id).all()

    return task