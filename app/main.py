from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import db_models
from .database import engine
from .routers import audit_logs, org, user, task,auth, assign_tasks, admin
import logging
from .models.config import Settings
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import time
import sys
settings = Settings()


#logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


#stream handler
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s  [%(levelname)s] - %(message)s ")
stream_handler.setFormatter(log_formatter)

# Add handler to the root logger so all loggers inherit it
logging.getLogger().addHandler(stream_handler)

logger.info("starting fast api")



#create database
db_models.Base.metadata.create_all(bind=engine)

#Initialize FastAPI
app = FastAPI(
    title="Texoc Task Manager API",
    description="API for managing tasks, users, and organizations.",
    version="1.0.0"
)



# Add CORS middleware - ADD THIS SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

### Limiter instance for rate limiting API requests
limiter = Limiter(
    key_func= get_remote_address, #rate limit by ip address
    storage_uri = settings.redis_url if settings.redis_url else None,
    default_limits = ["1000/day", "100/hour"]
)

##adding the limiter to the router
app.state.limiter = limiter

#custom rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc:RateLimitExceeded):
    return JSONResponse(status_code=429, content={
        "detail": "Too many attempts. Please try again later.",
        "retry_after": exc.retry_after,
        "time": int(time.time())
    })



"""routers"""
app.include_router(org.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(auth.router)
app.include_router(assign_tasks.router)
app.include_router(audit_logs.router)
app.include_router(admin.router)