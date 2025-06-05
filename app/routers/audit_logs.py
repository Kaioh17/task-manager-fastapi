from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
from datetime import datetime, timedelta
from uuid import uuid4

from typing import Optional
from fastapi import File, UploadFile,Form
from .celery_task import delete_row,add_rows

router = APIRouter(
    prefix = "/audit-log",
    tags=["audit-log"]
)

##Admin approval
@router.patch("/approve", status_code=status.HTTP_201_CREATED)
async def approve_task(payload: schemas.Approved,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ##we want to approve of the tasks and have it deleted from the database after 24hours.
    #timed delete with redis 
    ##confirmation email will be sent to the user(subordinate) assigned to the task 

    if current_user.user_role != "admin":
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail =f"User level not authorized")

    approve_query = db.query(db_models.AuditLog).filter(db_models.AuditLog.assignment_id == payload.assignment_id)
    approve_data = approve_query.first()

    if not approve_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Assignment with {payload.assignment_id} ")
    
    if approve_data.approved_by:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"Assignment is already approved") 

    approve_query.update({"approved_by": current_user.user_id})
    
    db.commit()
    approve_data_first = approve_query.first()
    if approve_data.approved_by is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approved_by is missing but missing")
    
    if approve_data.assigned_on is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assigned_on is missing but missing")
    archive_entry = {
                "assignment_id" : approve_data.assignment_id, 
                "task_id" : approve_data.task_id,
                "org_id" : approve_data.org_id,
                "user_id" : approve_data.user_id,
                "task_name" : approve_data.task_name, 
                "task_description" : approve_data.task_description,
                "task_status" : approve_data.task_status,
                "proof_of_completion" : approve_data.proof_of_completion,
                "completed_on" : str(approve_data_first.completed_on),
                "approved_by" : approve_data_first.approved_by,
                "assigned_on" : str(approve_data_first.assigned_on),
            }
    
    print(archive_entry)
    print(f"approved_by: {approve_data.approved_by},assigned_on: {str(approve_data.assigned_on)} ")
    # db.refresh(approve_data)
    # db.delete(approve_data)
    # db.commit()
   
    # print(f"assignment id: {approve_data.assignment_id}")
    add_rows.apply_async(args = ["approved_task_archives",archive_entry], countdown=30)
    delete_row.apply_async(args = ["audit_log", payload.assignment_id], countdown=35)
   
    #delete_row.apply_async(args = ["task_assignment",assignment.assignment_id], countdown=60)


    return({"msg": f"Task approved by {current_user.user_id}"})