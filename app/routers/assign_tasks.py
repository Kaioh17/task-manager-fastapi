from fastapi import APIRouter,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from ..core import oauth2

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import Optional
from fastapi import File, UploadFile,Form
from ..services import assign_tasks_service

"""
This module provides endpoints for assigning tasks, displaying assigned tasks, 
and marking tasks as complete. These endpoints are primarily used by admin users 
of an organization to manage tasks for their subordinates.
"""

router = APIRouter(
    prefix="/assigned",
    tags= ['Assigned']
)

@router.get("/", status_code=status.HTTP_200_OK, response_model= list[schemas.AssignedTaskOut])
def assigned_tasks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ### returns all tasks assigned for that user    
    ass_tasks = db.query(db_models.TaskAssignment).filter(db_models.TaskAssignment.user_id == current_user.user_id).all()

    return ass_tasks


### for admin, manager use only
@router.post("/",  status_code=status.HTTP_201_CREATED,  response_model= schemas.AssignedTaskOut)
def assign_tasks(tasks: schemas.AssignTask,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): 

    assign_task = assign_tasks_service.assign_task(current_user, tasks, db)
    return assign_task

@router.patch("/{assignment_id}/status", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.AssignedTaskOut)
async def update_task_status(assignment_id: int, 
                             task_status: str = Form(...), proof_of_completion: Optional[UploadFile] = File(None),
                             db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):
    
    assignment = await assign_tasks_service.update_task_status(assignment_id, task_status, proof_of_completion, db, current_user)
    return assignment
