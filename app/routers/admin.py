from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
from .. import utils
from ..core import oauth2
from datetime import datetime, timedelta
import os
from uuid import uuid4
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from ..services import admin_services
from typing import Optional
from fastapi import File, UploadFile,Form
from .celery_task import delete_row,add_rows

"""
This module provides endpoints specific to only admins 
"""

router = APIRouter(
    prefix="/admin",
    tags= ['Admin']
)

@router.get("/users", response_model=list[schemas.UserOut], status_code=status.HTTP_200_OK)
def users(db: Session = Depends(get_db), current_user: int  = Depends(oauth2.get_current_user)):
    """gets all users under admin"""
    users = admin_services.get_all_users(db, current_user)

    return users
#create an admin
@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.CreateAdmin, db:Session = Depends(get_db)):
    logger.info(f"Creating user with email: {user.user_email}")
    try:
        user_query = admin_services.create_admin(user, db, utils)
    except Exception as e:
        logger.warning(str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    logger.info(f"User created with user_id={user_query.user_id}")

    return user_query

@router.patch("/promote/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def promote_users_(user_id: int, promote: schemas.PromoteUser, db: Session = Depends(get_db), 
           current_user: int = Depends(oauth2.get_current_user)):
    
    logger.info(" Promoting...")
    user = admin_services.promote_users(user_id, promote, db, current_user)


    return{"msg": f"user: {user.first_name},{user.last_name} has been promoted!!!"}


@router.patch("/settings",response_model=schemas.org_settings, status_code=status.HTTP_202_ACCEPTED)
def update_org_settings(setting: schemas.org_settings,
                 db:Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    """Admin will set organiztions default settings here"""
    updated_settings = admin_services.update_settings(db, current_user, setting)
    return updated_settings