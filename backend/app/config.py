from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "ERP System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://erp_user:erp_password@localhost:5432/erp_db"
    DATABASE_URL_SYNC: str = "postgresql://erp_user:erp_password@localhost:5432/erp_db"

    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    REDIS_URL: str = "redis://localhost:6379/0"

    LOW_STOCK_THRESHOLD: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
