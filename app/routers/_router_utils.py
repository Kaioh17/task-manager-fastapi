from fastapi import HTTPException, status

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#admin only
def _ensure_admin_user(current_user):
     if current_user.user_role != "admin":
        logger.warning(f"Unauthorized attempt by user_id={current_user.user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied: role not authorized")
#admin and manager user
def _ensure_not_regular_user(current_user):
     if current_user.user_role == "user":
        logger.warning(f"Unauthorized attempt by user_id={current_user.user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied: role not authorized")
