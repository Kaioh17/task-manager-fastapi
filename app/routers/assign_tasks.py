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
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import Optional
from fastapi import File, UploadFile,Form
from .celery_task import delete_row,add_rows

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
                             current_user: int = Depends(oauth2.get_current_user)):
    logger.info(f"User {current_user.user_id} attempting to update status for assignment {assignment_id}.")
    assigned_task = db.query(db_models.TaskAssignment).filter(db_models.TaskAssignment.assignment_id == assignment_id)
    assignment = assigned_task.first()

    
    if not assignment:
        logger.warning(f"Task with id {assignment_id} does not exist.")
        raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Task with id: {assignment_id} does not exist"
                    )
    
    if task_status.lower() != "complete":
        logger.warning(f"Invalid task status '{task_status}' received for assignment {assignment_id}.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid task status: '{task_status}'. Only 'complete' is allowed."
        )
        print(f"Debug: Received invalid task_status value: {task_status}")

    assigned_task.update({"task_status":task_status.lower()})
    logger.info(f"Updated task_status to '{task_status.lower()}' for assignment {assignment_id}.")

    get_due_date = assignment.due_date
    if datetime.utcnow() > get_due_date:
        logger.warning(f"Task {assignment_id} is past due date.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail = f"Task is past due date")
    db.commit()
    #Adding files
    file_path = None
    if proof_of_completion:
        ALLOWED_TYPES = [
            "image/png", "image/jpeg", "application/pdf",
            "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        if proof_of_completion.content_type not in ALLOWED_TYPES:
            logger.warning(f"File type {proof_of_completion.content_type} not supported for assignment {assignment_id}.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File type not supported')

        UPLOAD_DIR = "proofs/"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_ext = os.path.splitext(proof_of_completion.filename)[-1]
        file_path = os.path.join(UPLOAD_DIR, f"{uuid4()}{file_ext}")
        try:

            MAX_FILE_SIZE_MB = 10
            if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
                logger.warning(f"File too large for assignment {assignment_id}.")
                raise HTTPException(status_code=400, detail="File too large")
            
            contents = await proof_of_completion.read()
            with open(file_path, "wb") as f:
                f.write(contents)

           
        except Exception as e:
            logger.error(f"File upload failed for assignment {assignment_id}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File upload failed: {str(e)}")
        assigned_task.update({"proof_of_completion": file_path})
        logger.info(f"Proof of completion uploaded for assignment {assignment_id} at {file_path}.")
    else:
        assigned_task.update({"proof_of_completion": None})
        logger.info(f"No proof of completion provided for assignment {assignment_id}.")

    db.commit()
    logger.info(f"Database commit complete for assignment {assignment_id}.")
    
    db.refresh(assignment)
    ##move to audit_log tbale
    if assignment.task_status.lower() == "complete":
        audit_entry = {
                "assignment_id" : assignment.assignment_id, 
                "task_id" : assignment.task_id,
                "org_id" : assignment.task.org_id,
                "user_id" : assignment.user_id,
                "task_name" : assignment.task.task_name, 
                "task_description" : assignment.task.task_description,
                "task_status" : assignment.task_status,
                "proof_of_completion" : assignment.proof_of_completion,
                "assigned_on" : str(assignment.created_on)
        }
        logger.info(f"Archiving completed assignment {assignment_id} to audit_log.")
        add_rows.apply_async(args = ["audit_log", audit_entry], countdown = 30)
        logger.info(f"Scheduled deletion of completed assignment {assignment_id} from task_assignment.")
        delete_row.apply_async(args = ["task_assignment",assignment.assignment_id], countdown=60)
    return assignment

