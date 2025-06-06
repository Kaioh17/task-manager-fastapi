from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
import logging

router = APIRouter(
    prefix = "/user",
    tags = ['Users']
)



##get all users
@router.get('/', status_code = status.HTTP_200_OK, response_model=list[schemas.UserOut])
def users(db: Session =  Depends(get_db)):
    logging.info("Fetching all users from the database.")
    user = db.query(db_models.Users).all()
    logging.info(f"Fetched {len(user)} users.")
    return user

##get user by id
@router.get('/{user_id}', status_code = status.HTTP_202_ACCEPTED, response_model=schemas.UserOut)
def user_id(user_id: int, db: Session = Depends(get_db)):
    logging.info(f"Fetching user with user_id={user_id}.")
    user = db.query(db_models.Users).filter(db_models.Users.user_id == user_id).first()
    if not user:
        logging.warning(f"User with user_id={user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="users {org_id} not found")
    logging.info(f"User with user_id={user_id} found.")
    return user

## get all users in organization id
@router.get('/organization/{org_id}', status_code = status.HTTP_202_ACCEPTED, response_model=schemas.UserOut)
def user_org_id(org_id: int, db: Session = Depends(get_db)):
    logging.info(f"Fetching users for organization org_id={org_id}.")
    user = db.query(db_models.Users).filter(db_models.Users.org_id == org_id).all()
    if not user:
        logging.warning(f"No users found for organization org_id={org_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organization {org_id} not found")
    logging.info(f"Fetched {len(user)} users for organization org_id={org_id}.")
    return user

#create a user
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.CreateUser, db:Session = Depends(get_db)):
    logging.info(f"Creating user with email: {user.user_email}")
    ##hash passwords
    hashed_password = utils.hash(user.user_password)
    user.user_password = hashed_password

    validate_org = _validate_organization(user.org_id, db)
    user.org_id = validate_org

    user_query = db_models.Users(**user.dict())

    db.add(user_query)
    db.commit()
    db.refresh(user_query)
    logging.info(f"User created with user_id={user_query.user_id}")
    return user_query

#delete user account 
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(confirm: schemas.DeleteUser ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    logging.info(f"Attempting to delete user_id={current_user.user_id}")
    # confirm password before deleting account
    if not utils.verify(confirm.user_password, current_user.user_password):
        logging.warning(f"Failed authentication for user_id={current_user.user_id} during delete attempt.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication not recognized!!")
    user_query = db.query(db_models.Users).filter(db_models.Users.user_id == current_user.user_id)
    user_query.delete(synchronize_session = False)
    db.commit()
    logging.info(f"User with user_id={current_user.user_id} deleted.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    


##helper function to verify organization
def _validate_organization(org: int,  db: Session = Depends(get_db)):
    ##check if user exists
    org_query = db.query(db_models.Organizations).filter(db_models.Organizations.org_id == org).first()
    if not org_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organization {org} does not exist")
    
    return org

