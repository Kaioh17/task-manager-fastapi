# Service layer for org router
from ..models import db_models
from fastapi import HTTPException, status
from ..redis_connection import redis_client
import secrets 
import base64
# from ..utils import hash_token 
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_organizations(db):
    org = db.query(db_models.Organizations).all()   
    return org

def get_organization_by_id(org_id: int, db):
    get_token(org_id)
    org = db.query(db_models.Organizations).filter(db_models.Organizations.org_id == org_id).first()
    return org



"""Organization helper functions"""

def generate_org_token(length = 6):
    logger.info("Creating token...")
    token = secrets.token_bytes(5)

    return base64.b32encode(token).decode("utf-8")[:length].lower()

def _redis(org_id, token):
    logger.info("saving token...")
    # redis_client.set(f"org_token:{org_id}", token, ex=864000)  #for production level
    redis_client.set(f"org_token:{org_id}", token)

    logger.info("token Saved")


def verify_token_exist(org_id):
    logger.info("checking for token...")
    verify = redis_client.exists(f"org_token:{org_id}")
    logger.info("token exists.")

    if verify != 1:
        logger.warning(f"No token saved for this organization{org_id}")
        raise HTTPException(status_code=404)
    
def get_token(org_id):
        token = redis_client.get(f"org_token:{org_id}")
        if token: 
            token = token.decode("utf-8")
            logger.info(f"Token found {token}")
        
        return token


        