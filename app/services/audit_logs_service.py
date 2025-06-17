# Service layer for audit_logs router
from ..models import db_models
from fastapi import HTTPException, status
from ..routers import _router_utils

def approve_task_service(assigned_id: int, db, current_user, add_rows, delete_row, logger):
    logger.info(f"User {current_user.user_id} attempting to approve assignment {assigned_id}.")
    _router_utils._ensure_not_regular_user(current_user)

    approve_query = db.query(db_models.AuditLog).filter(db_models.AuditLog.assignment_id == assigned_id)
    approve_data = approve_query.first()

    #validate assignment_id 
    if not approve_data:
        logger.warning(f"Assignment {assigned_id} not found for approval.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Assignment with {assigned_id} ")
    
    if approve_data.approved_by:
        logger.warning(f"Assignment {assigned_id} is already approved.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"Assignment is already approved") 

    approve_query.update({"approved_by": current_user.user_id})
    db.commit()
    logger.info(f"Assignment {assigned_id} approved by user {current_user.user_id}.")

    approve_data_first = approve_query.first()
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
    logger.info(f"Archiving assignment {assigned_id} to approved_task_archives.")
    add_rows.apply_async(args = ["approved_task_archives",archive_entry], countdown=30)
    logger.info(f"Scheduled deletion of assignment {assigned_id} from audit_log.")
    delete_row.apply_async(args = ["audit_log", assigned_id], countdown=35)
    return current_user