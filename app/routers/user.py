from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
from ..services import user_service
import logging


router = APIRouter(
    prefix = "/user",
    tags = ['Users']
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

##get all users
@router.get('/', status_code = status.HTTP_200_OK, response_model=list[schemas.UserOut])
def users(db: Session =  Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    logger.info("Fetching all users from the database.")
    if current_user.user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only for authorized users")
    user = db.query(db_models.Users).all()
    logger.info(f"Fetched {len(user)} users.")
    return user

@router.get('/organizations', response_model=list[schemas.OrgOut])
def get_organizations(db: Session = Depends(get_db)):
    return db.query(db_models.Organizations).all()

@router.get('/organization/{org_id}', status_code = status.HTTP_202_ACCEPTED, response_model=list[schemas.UserOut])
def user_org_id(org_id: int, db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user) ):
    logger.info(f"Fetching users for organization org_id={org_id}.")
    if current_user.user_role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only for authorized users")

    users = user_service.get_users_by_org_id(org_id, db)
    # users = db.query(db_models.Users).filter(db_models.Users.org_id == org_id).all()
    if not users:
        logger.warning(f"No users found for organization org_id={org_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organization {org_id} not found")
    logger.info(f"Fetched {len(users)} users for organization org_id={org_id}.")
    return users

#create a user
@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.CreateUser, db:Session = Depends(get_db)):
    logger.info(f"Creating user with email: {user.user_email}")
    try:
        user_query = user_service.create_user_service(user, db, utils)
    except Exception as e:
        logger.warning(str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    logger.info(f"User created with user_id={user_query.user_id}")
    return user_query

#delete user account 
@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(confirm: schemas.DeleteUser ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    logger.info(f"Attempting to delete user_id={current_user.user_id}")
    try:
        user_service.delete_user_service(confirm, db, current_user, utils)
    except Exception as e:
        logger.warning(str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    logger.info(f"User has been deleted.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)