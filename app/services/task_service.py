# Service layer for Task router
from ..models import db_models
from fastapi import HTTPException, status


def create_task_service(current_user,task,db):

    task_query = db_models.Tasks(org_id = current_user.org_id, **task.dict())
    db.add(task_query)
    db.commit()
    db.refresh(task_query)

    return task_query

def get_task_service(db, current_user):
    if current_user.user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Access denied: insufficient role")
    task = db.query(db_models.Tasks).filter(db_models.Tasks.org_id == current_user.org_id).all()
    return task