import hashlib
from fastapi import APIRouter, HTTPException,status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.params import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..models import db_models,schemas
from ..database import get_db
from..core import oauth2
from .. import utils
from ..models.config import Settings
from datetime import time
from ..redis_connection import redis_client
import logging
# logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)
settings = Settings()
### Limiter instance for rate limiting API requests
limiter = Limiter(
    key_func= get_remote_address, #rate limit by ip address
    storage_uri = settings.redis_url if settings.redis_url else None,
    default_limits = ["1000/day", "100/hour"]
)


router = APIRouter(
    tags = ['Authentication']
)
# #custom rate limit error handler
# def setup_rate_limiter_handler(app):
#     @router.exception_handler(RateLimitExceeded)
#     async def rate_limit_handler(request: Request, exc:RateLimitExceeded):
#         return JSONResponse(status_code=429, content={
#             "detail": "Too many login attempts. Please try again later.",
#             "retry_after": exc.retry_after,
#             "time": int(time.time())
#         })


"""Helper Fynctions"""
def get_user_rate_limit_key(email: str, ip: str) -> str:
    """create unique key for user and ip combined"""
    combined = f"{email}:{ip}"
    return hashlib.md5(combined.encode()).hexdigest()

def check_user_specific_rate_limit(email:str, ip:str, max_attempts: int = 3, window_minutes: int = 5):
    """Check and updates user-specific rate limiting"""
    user_key = get_user_rate_limit_key(email, ip)
    attempts_key = f"login_attempts:{user_key}"
    
    current_attempts = redis_client.get(attempts_key)
    print(f"current_attempts = {current_attempts} --line 60")
    if current_attempts and int(current_attempts) >= max_attempts:
        ttl = redis_client.ttl(attempts_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail = f"To many failed login attempts. Try again in {ttl} seconds."
        )
    return attempts_key

def record_failed_attempt(attempts_key: str, window_minutes: int = 5):
    """record a failed login attempt"""
    pipe = redis_client.pipeline()
    pipe.incr(attempts_key)
    pipe.expire(attempts_key, window_minutes * 60)
    pipe.execute()                

def clear_failed_attempts(attempts_key: str):
    """clear failed attempts on successful login"""
    redis_client.delete(attempts_key)


@router.post('/login')
## we will be verifying using the email provided by the user
def login(request:Request ,user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    logging.info(f"Log in process started for user {user_credentials.username}")

    #get clients IP for rate limiting
    client_ip =  get_remote_address(request)

    #check user-specific rate limiting 
    attempts_key= check_user_specific_rate_limit(
        email=user_credentials.username,
        ip = client_ip,
        max_attempts=3,
        window_minutes=5
    )
    print(attempts_key)
    ##check if user exist
    user = db.query(db_models.Users).filter(db_models.Users.user_email == user_credentials.username).first()
    #verify email exists
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "invalid credentials")
    
    ##verify password matches database
    if not utils.verify(user_credentials.password, user.user_password):
        record_failed_attempt(attempts_key)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "invalid credentials")
    
    clear_failed_attempts(attempts_key)

    ##get token
    access_token = oauth2.create_access_token(data = {"user_id": user.user_id, "user_email": user.user_email})
    

    logging.info(f"Successful login for user: {user.first_name}{user.last_name}")
    return {"access_token": access_token,
             "token_type": "bearer"}


