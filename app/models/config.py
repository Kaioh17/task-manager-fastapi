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
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "db"  # Docker service name
    db_port: int = 5432
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET: str
        
  

    class Config:
        env_file = ".env"
        # ec2_env_file = ".env.ec2"

