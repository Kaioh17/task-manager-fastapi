from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2

"""Assign task endpoint will be used to display, add and complete tasks, assigned by an admin user of an organization"""

router = APIRouter(
    prefix="/assigned"
)

@router.get("/", status_code=status.HTTP_200_OK, response_model= list[schemas.AssignedTaskOut])
def assigned_tasks(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ### returns all tasks assigned for that user    
    ass_tasks = db.query(db_models.TaskAssignment).filter(db_models.TaskAssignment.user_id == current_user.user_id).all()

    return ass_tasks


### for admin use only
@router.post("/",  status_code=status.HTTP_201_CREATED,  response_model= schemas.AssignedTaskOut)
def assign_tasks(tasks: schemas.AssignTask,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ### assign tasks to subordinate of organizations by providing user_id 
    ##when admin provides the task_id it fetches the name and descriptio n of the tasks 
    #assigns to the user 

    role  =  current_user.user_role  
    if role.lower() != "admin":  ## confirm user role
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail = "Access denied: role not authorized")

    #how do we send the name of a t
    tasks_record = db.query(db_models.Tasks).filter(db_models.Tasks.task_id == tasks.task_id).first()
    print(tasks_record.task_name)
    print(tasks_record.task_description)


    assign_task = db_models.TaskAssignment(  
                                    org_id = current_user.org_id, 
                                    assigned_by_id = current_user.user_id,
                                    task_name = tasks_record.task_name,
                                    task_description = tasks_record.task_description, 
                                    **tasks.dict()
                                )
    
    db.add(assign_task)
    db.commit()
    db.refresh(assign_task)
    

    return assign_task

@router.patch("/", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.AssignedTaskOut)
def update_task_status(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    pass