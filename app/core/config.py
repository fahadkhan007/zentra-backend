from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    PROJECT_NAME: str = "Zentra ML API"
    ENVIRONMENT: str = "development"

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    
    
    # Database
    DATABASE_URL: PostgresDsn

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


    #redis
    REDIS_HOST: str="localhost"
    REDIS_PORT: int=6379


settings = Settings() #type: ignore
