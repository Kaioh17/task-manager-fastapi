# Service layer for admin router
from ..models import db_models
from fastapi import HTTPException, status
from ..routers import _router_utils
from ..models import schemas
from .org_service import generate_org_token, _redis
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""Admin only services"""
def create_admin(user: 'schemas.CreateAdmin', db, utils):
    """Service function to create a new admin_users."""
    validate_user = db.query(db_models.Users).filter(db_models.Users.user_email == user.user_email).first()
    if validate_user:
        raise Exception("user with email already exists")


    ##query the organization
    org_query = db_models.Organizations(org_name = user.org_name,
                                        org_description = user.org_description)
    db.add(org_query)
    db.commit()
    db.refresh(org_query)
    
    org = db.query(db_models.Organizations).filter(db_models.Organizations.org_name == user.org_name).first()
    get_org_id = org.org_id

    #Set organization token
    token = generate_org_token(6)
    _redis(get_org_id, token)

    #default org settings
    set_org_settings(db, get_org_id)

    user_query = db_models.Users(
                                org_id = get_org_id,
                                first_name = user.first_name,
                                 last_name = user.last_name,
                                 user_email = user.user_email,
                                 user_password = user.user_password,
                                 user_role = user.user_role
                                 )
    
    hashed_password = utils.hash(user.user_password)
    # user_query = db_models.Users(**user.model_dump())
    user_query.user_password = hashed_password

    db.add(user_query)
    db.commit()
    db.refresh(user_query)
    return user_query

def get_all_users(db, current_user):
    _router_utils._ensure_not_regular_user(current_user)
    _router_utils._ensure_manager_clearabce_not_low(current_user, db_models)

    logger.info(f"Fetching all users for org_id={current_user.org_id} by user_id={current_user.user_id}")
    user_query = db.query(db_models.Users).filter(db_models.Users.org_id == current_user.org_id)
    users = user_query.all()

    logger.debug(f"Found {len(users)} users for org_id={current_user.org_id}")
    return users

def promote_users(user_id: int, promote, db, current_user):
    _router_utils._ensure_admin_user(current_user)
    
    """promote users to to manager"""
    if not user_id:
        logger.warning("Promotion attempt with missing user_id")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_query = db.query(db_models.Users).filter(db_models.Users.user_id == user_id)
    user = user_query.first()


    if not user:
        logger.warning(f"Promotion attempt for non-existent user_id={user_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    logger.info(f"Promoting user_id={user_id} to role={promote.user_role.lower()} by admin_id={current_user.user_id}")
    user_query.update({"user_role": promote.user_role.lower()})
    db.commit()
    return user

"""update settings"""
def update_settings(db, current_user, setting):
    _router_utils._ensure_admin_user(current_user)

    logger.info(f"Admin user_id={current_user.user_id} attempting to update settings for org_id={current_user.org_id}")

    get_settings = db.query(db_models.OrgSettings).filter(db_models.OrgSettings.org_id == current_user.org_id)
    settings_update = get_settings.first()
    if not settings_update:
        logger.warning(f"No settings found for org_id={current_user.org_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")

    get_settings.update({"settings": setting.settings.model_dump()})
    db.commit()

    logger.info(f"Settings updated for org_id={current_user.org_id} by user_id={current_user.user_id}")

    return settings_update    

"""Organization default settings"""
def set_org_settings(db, org_id):
    logger.info(f"Setting default organization settings for org_id={org_id}")

    default_settings = {
        "manager_clearance": "medium"
    }

    try:
        setting_query = db_models.OrgSettings(org_id=org_id, settings=default_settings)
        db.add(setting_query)
        db.commit()
        db.refresh(setting_query)
        logger.info(f"Default settings set for org_id={org_id}")
        return setting_query
    except Exception as e:
        logger.warning(f"Failed to set default settings for org_id={org_id}: {e}")
        db.rollback()
        raise 


    

