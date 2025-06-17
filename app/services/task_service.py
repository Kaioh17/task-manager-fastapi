# Service layer for Task router
from ..models import db_models
from fastapi import HTTPException, status
from ..routers import _router_utils
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""Task service router"""
def create_task_service(current_user, task, db):
    logger.info(f"Creating task for org_id={current_user.org_id} by user_id={current_user.user_id}")
    task_query = db_models.Tasks(org_id=current_user.org_id, **task.dict())
    db.add(task_query)
    db.commit()
    db.refresh(task_query)
    logger.info(f"Task created with task_id={task_query.task_id}")
    return task_query

def get_task_service(db, current_user):
    _router_utils._ensure_not_regular_user(current_user)
    logger.info(f"Fetching tasks for org_id={current_user.org_id} by user_id={current_user.user_id}")
    task = db.query(db_models.Tasks).filter(db_models.Tasks.org_id == current_user.org_id).all()
    logger.info(f"Fetched {len(task)} tasks")
    return task

def del_task_service(db, current_user, task_id: int):
    _router_utils._ensure_not_regular_user(current_user)
    logger.info(f"Attempting to delete task_id={task_id} by user_id={current_user.user_id}")
    task_query = db.query(db_models.Tasks).filter(db_models.Tasks.task_id == task_id)
    task = task_query.first()

    if not task:
        logger.warning(f"Task with task_id={task_id} not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with {task_id} not found")

    logger.info(f"Deleting task_id={task_id}")
    task_query.delete(synchronize_session=False)
    db.commit()
    logger.info(f"Task with task_id={task_id} deleted successfully")
    return task