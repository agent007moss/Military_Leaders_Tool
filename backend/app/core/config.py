from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    env: str = "dev"
    database_url: str

    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_expires_min: int = 60

    owner_override_enabled: bool = True

    upload_storage_dir: str = "./storage"
    max_uploads_per_spot: int = 3

settings = Settings()