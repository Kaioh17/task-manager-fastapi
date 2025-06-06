from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
from datetime import datetime, timedelta
from uuid import uuid4
import logging

from typing import Optional
from fastapi import File, UploadFile,Form
from .celery_task import delete_row,add_rows



router = APIRouter(
    prefix = "/audit-log",
    tags=["audit-log"]
)

##Admin approval
@router.patch("/approve/{assigned_id}", status_code=status.HTTP_201_CREATED)
async def approve_task(assigned_id: int,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ###Improve approval stage by giving the ability to reject tasks and return back to the assigned user with comments

    logging.info(f"User {current_user.user_id} attempting to approve assignment {assigned_id}.")
    if current_user.user_role != "admin":
        logging.warning(f"User {current_user.user_id} is not authorized to approve assignments.")
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail =f"User level not authorized")

    approve_query = db.query(db_models.AuditLog).filter(db_models.AuditLog.assignment_id == assigned_id)
    approve_data = approve_query.first()

    #validate assignment_id 
    if not approve_data:
        logging.warning(f"Assignment {assigned_id} not found for approval.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Assignment with {assigned_id} ")
    
    if approve_data.approved_by:
        logging.warning(f"Assignment {assigned_id} is already approved.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"Assignment is already approved") 

    approve_query.update({"approved_by": current_user.user_id})
    db.commit()
    logging.info(f"Assignment {assigned_id} approved by user {current_user.user_id}.")

    approve_data_first = approve_query.first()
    # if approve_data.approved_by is None:
    #     logging.error(f"approved_by is missing after approval for assignment {payload.assignment_id}.")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="approved_by is missing but missing")
    
    # if approve_data.assigned_on is None:
    #     logging.error(f"assigned_on is missing for assignment {payload.assignment_id}.")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assigned_on is missing but missing")
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
    logging.info(f"Archiving assignment {assigned_id} to approved_task_archives.")
    add_rows.apply_async(args = ["approved_task_archives",archive_entry], countdown=30)
    logging.info(f"Scheduled deletion of assignment {assigned_id} from audit_log.")
    delete_row.apply_async(args = ["audit_log", assigned_id], countdown=35)
    return({"msg": f"Task approved by {current_user.user_id}"})