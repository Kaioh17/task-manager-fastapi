from pydantic_settings import BaseSettings


##clean build for the api access the env file
class Settings(BaseSettings):
    db_url: str
    secret_key: str

    class Config:
        env_file = "app/.env"

