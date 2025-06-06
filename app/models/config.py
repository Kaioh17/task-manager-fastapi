from pydantic import Field
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    db_url: str
    secret_key: str = Field(min_length=32)
    algorithm: str
    access_token_expire_minutes: int
    host: str
    redis_port: int
    redis_url: str
    
  

    class Config:
        env_file = "app/.env"

