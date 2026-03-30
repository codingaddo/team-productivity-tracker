from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///./app.db")
    jwt_secret: str = os.getenv("JWT_SECRET", os.getenv("AUTH_SECRET", "dev-secret"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
