from fastapi import APIRouter, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from ..models import db_models,schemas
from ..database import get_db
from..core import oauth2
from .. import utils

router = APIRouter(
    tags = ['Authentication']
)

@router.post('/login')
## we will be verifying using the email provided by the user
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ##check if user exists
    user = db.query(db_models.Users).filter(db_models.Users.user_email == user_credentials.username).first()
    print(user)
    #verify email exists
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "invalid credentials")
    
    ##verify password matches database
    if not utils.verify(user_credentials.password, user.user_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "invalid credentials")
    
    ##get token
    access_token = oauth2.create_access_token(data = {"user_id": user.user_id, "user_email": user.user_email})
    
    return {"access_token": access_token, "token_type": "bearer"}


