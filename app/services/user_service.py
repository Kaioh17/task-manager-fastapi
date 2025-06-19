# Service layer for user router
from ..models import db_models
from fastapi import HTTPException, status
from .org_service import verify_token_exist, get_token
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_users_by_org_id(org_id: int, db):
    """Service function to fetch users by organization id."""
    users = db.query(db_models.Users).filter(db_models.Users.org_id == org_id).all()
    return users


def get_users_by_user_id(user_id: int, db):
    """service function to fetch users by user id"""
    users = db.query(db_models.Users).filter(db_models.Users.user_id == user_id).first()
    return users


def create_user_service(user: 'schemas.CreateUser', db, utils):
    """Service function to create a new user."""
    # if user.user_role == "admin":
    #     return create_user_service_admin(user, db, utils)
    _validate_user(user, db)
   
    hashed_password = utils.hash(user.user_password)
    user_query = db_models.Users(**user.model_dump(exclude ={"org_token"}))
    user_query.user_password = hashed_password


    ##validate organnization token 
    _validate_organization(user.org_id,user.org_token,db)


    db.add(user_query)
    db.commit()
    db.refresh(user_query)
    return user_query

def _validate_user(user,db):
    validate_user = db.query(db_models.Users).filter(db_models.Users.user_email == user.user_email).first()
    if validate_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT
                            ,detail= "user with email already exists")




def delete_user_service(confirm, db, current_user, utils):
    """Service function to delete a user account after password confirmation."""
    if not utils.verify(confirm.user_password, current_user.user_password):
        raise Exception("Authentication not recognized!!")
    user_query = db.query(db_models.Users).filter(db_models.Users.user_id == current_user.user_id)
    user_query.delete(synchronize_session = False)
    db.commit()
    return True

##helper function to verify organization
def _validate_organization(org_id: int, org_token: str,  db):
    ##check if organization exists
    verify_token_exist(org_id) #verifies the organization
    token = get_token(org_id)

    if token != org_token:
        logger.warning("Incorrect Token!!")
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail = "Incorrect Token - Confirm token with admin")
    

    
    