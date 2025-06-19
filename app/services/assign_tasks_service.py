# Service layer for assign_tasks router
from ..models import db_models
from fastapi import HTTPException, status
from ..routers import _router_utils
from datetime import timedelta, datetime
import os
from uuid import uuid4
from app.routers.celery_task import delete_row,add_rows


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def assign_task(current_user, tasks, db):

    logger.info("Assigning tasks...")
    _router_utils._ensure_not_regular_user(current_user)
    _router_utils._validate_user(db_models, tasks.user_id, db)

    


    tasks_query = db.query(db_models.Tasks).filter(db_models.Tasks.task_id == tasks.task_id)
    task = tasks_query.first()

    #check if task has already been assigned 
    

    if not task:
        logger.info(f"Task {tasks.task_id} does not exists")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    logger.info(f"Task_records: {task.task_id}")


    assign_task = db_models.TaskAssignment(  
                                    org_id = current_user.org_id, 
                                    assigned_by_id = current_user.user_id,
                                    task_name = task.task_name,
                                    task_description = task.task_description, 
                                    **tasks.dict()
                                )
    
    ##check if due_date is valid (set at least 1 hour after current time)
    offset = datetime.utcnow() + timedelta(hours=1)
    if tasks.due_date < offset:
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY, detail="Date and time not valid")
    
    db.add(assign_task)
    db.commit()
    db.refresh(assign_task)
    
    logger.info(f"Task {task.task_name} has been assigned too {tasks.user_id}")

    return assign_task

def update_task_status(assignment_id, task_status, proof_of_completion, db, current_user):
    

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
        logger.info(f"Debug: Received invalid task_status value: {task_status}")

    assigned_task.update({"task_status":task_status.lower()})
    logger.info(f"Updated task_status to '{task_status.lower()}' for assignment {assignment_id}.")

    get_due_date = assignment.due_date
    if datetime.utcnow() > get_due_date:
        logger.warning(f"Task {assignment_id} is past due date.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail = f"Task is past due date")
    db.commit()

    add_files(db,  assigned_task, proof_of_completion, assignment_id)
    
    
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


async def add_files(db,assigned_task,proof_of_completion, assignment_id):
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

           
            contents = await proof_of_completion.read()

            MAX_FILE_SIZE_MB = 10
            if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
                logger.warning(f"File too large for assignment {assignment_id}.")
                raise HTTPException(status_code=400, detail="File too large")
            
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
    
   