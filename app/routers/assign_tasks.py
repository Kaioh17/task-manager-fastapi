from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
from datetime import datetime, timedelta
import os
from uuid import uuid4

from typing import Optional
from fastapi import File, UploadFile,Form

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

    print(f"Task_records: {tasks_record}")
    # print(tasks_record.task_description)


    assign_task = db_models.TaskAssignment(  
                                    org_id = current_user.org_id, 
                                    assigned_by_id = current_user.user_id,
                                    task_name = tasks_record.task_name,
                                    task_description = tasks_record.task_description, 
                                    **tasks.dict()
                                )
    
    ##check if due_date is valid (set at least 1 hour after current time)
    offset = datetime.utcnow() + timedelta(hours=1)
    if tasks.due_date < offset:
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY, detail="Date and time not valid")
    
    db.add(assign_task)
    db.commit()
    db.refresh(assign_task)
    
    return assign_task

@router.patch("/{assignment_id}/status", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.AssignedTaskOut)
async def update_task_status(assignment_id: int, 
                             task_status: str = Form(...), proof_of_completion: Optional[UploadFile] = File(None),
                             db: Session = Depends(get_db), 
                             current_user: int = Depends(oauth2.get_current_user)):##check if task is past due date
     ##timed delete using celery and redis
    

    assigned_task = db.query(db_models.TaskAssignment).filter(db_models.TaskAssignment.assignment_id == assignment_id) #get task
    assignment = assigned_task.first()

    if not assignment:
         raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Task with id: {assignment_id} does not exist"
                    )
    
    if task_status.lower() != "complete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid task status: '{task_status}'. Only 'complete' is allowed."
        )
        print(f"Debug: Received invalid task_status value: {task_status}")

    assigned_task.update({"task_status":task_status.lower()})

    ## check if task is still valid
    get_due_date = assignment.due_date

    if datetime.utcnow() > get_due_date:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail = f"Task is past due date")
    print(f"proof: {proof_of_completion}")
    file_path = None
    if proof_of_completion:
        # Validate file types
        ALLOWED_TYPES = [
            "image/png", "image/jpeg", "application/pdf",
            "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        if proof_of_completion.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File type not supported')

        UPLOAD_DIR = "proofs/"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_ext = os.path.splitext(proof_of_completion.filename)[-1]
        file_path = os.path.join(UPLOAD_DIR, f"{uuid4()}{file_ext}")
        try:
            contents = await proof_of_completion.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
        assigned_task.update({"proof_of_completion": file_path})
    else:
        # If proof is not required, set to None
        assigned_task.update({"proof_of_completion": None})

    db.commit()
    
    ##send to audit once task is set to complete 
    if assignment.task_status.lower() == "complete":
        audit_entry = db_models.AuditLog(assignment_id = assignment.assignment_id, 
                           task_id = assignment.task_id,
                           org_id = assignment.task.org_id,
                           user_id = assignment.user_id,
                            task_name = assignment.task.task_name, 
                            task_description = assignment.task.task_description,
                            task_status = assignment.task_status,
                            proof_of_completion = assignment.proof_of_completion,
                            assigned_on = assignment.created_on
                            )

      
  

    db.add(audit_entry)
    db.delete(assignment)
    db.commit()
    
    return assignment