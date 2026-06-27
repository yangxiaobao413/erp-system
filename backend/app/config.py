from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = 'ERP System'
    APP_VERSION: str = '1.0.0'
    DEBUG: bool = True

    DATABASE_URL: str = 'postgresql+asyncpg://erp_user:erp_password@localhost:5432/erp_db'
    DATABASE_URL_SYNC: str = 'postgresql://erp_user:erp_password@localhost:5432/erp_db'
    DATABASE_PUBLIC_URL: str = ''

    SECRET_KEY: str = '6RYyZkAK2p5j7cICJWerqHmEhlvMFfN0LoSOXuGQUxB9iT1DgPn4btaVz38dsw'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    REDIS_URL: str = 'redis://localhost:6379/0'
    LOW_STOCK_THRESHOLD: int = 10

    def model_post_init(self, __context) -> None:
        import os
        supabase_url = os.getenv('DATABASE_PUBLIC_URL', '')
        if supabase_url:
            self.DATABASE_URL = supabase_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
            self.DATABASE_URL_SYNC = supabase_url

        if self.DATABASE_URL.startswith('postgres://'):
            self.DATABASE_URL = self.DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
        if self.DATABASE_URL_SYNC.startswith('postgres://'):
            self.DATABASE_URL_SYNC = self.DATABASE_URL_SYNC.replace('postgres://', 'postgresql://', 1)

    class Config:
        env_file = '.env'
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
