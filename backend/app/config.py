from pydantic_settings import BaseSettings, SettingsConfigDict
from app.models.models import ROLE_ADMIN, ROLE_COACH


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite:///./boxingclub.db"
    JWT_SECRET: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = ""
    CORS_ORIGINS: str = "*"

    ROLE_ADMIN: str = ROLE_ADMIN
    ROLE_COACH: str = ROLE_COACH


settings = Settings()
