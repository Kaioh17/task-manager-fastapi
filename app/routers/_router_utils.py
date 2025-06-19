from fastapi import HTTPException, status

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _ensure_admin_user(current_user):
     if current_user.user_role != "admin":
        logger.warning(f"Unauthorized attempt by user_id={current_user.user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied: role not authorized")

def _ensure_not_regular_user(current_user):

     if current_user.user_role == "user":
        logger.warning(f"Unauthorized attempt by user_id={current_user.user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied: role not authorized")

def _ensure_manager_clearabce_not_low(current_user, db_models):
     get_clearance = db_models.OrgSettings.settings()
     manager_clearance = (
         get_clearance["manager_clearance"]
         if isinstance(get_clearance, dict)
         else getattr(get_clearance, "manager_clearance", None)
     )
     if current_user.user_role == "manager" and manager_clearance == "low":
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clearance not met")



def _ensure_manager_clearance_is_high(current_user, db_models):
     get_clearance = db_models.OrgSettings.settings()
     manager_clearance = (
         get_clearance["manager_clearance"]
         if isinstance(get_clearance, dict)
         else getattr(get_clearance, "manager_clearance", None)
     )
     if current_user.user_role == "manager" and manager_clearance != "high":
         logger.warning(f"unauthorized manager with '{manager_clearance}' clearance.")
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clearance not met")
     
def _validate_user(db_models, user_id, db):
      user_query = db.query(db_models.Users).filter(db_models.Users.user_id == user_id)
      user = user_query.first()

      if user is None:
          logger.warning(f"user {user_id} does not exists")
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
         