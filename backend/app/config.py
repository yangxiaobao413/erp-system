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

        def model_post_init(self, __context):`n        # Render PostgreSQL URL 兼容处理`n        if self.DATABASE_URL.startswith("postgres://"):`n            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)`n        if self.DATABASE_URL_SYNC.startswith("postgres://"):`n            self.DATABASE_URL_SYNC = self.DATABASE_URL_SYNC.replace("postgres://", "postgresql://", 1)`n`n    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
