from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents:
# [0]=core, [1]=app, [2]=backend, [3]=repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPO_ROOT / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "dev"
    database_url: str

    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_expires_min: int = 60

    owner_override_enabled: bool = True

    upload_storage_dir: str = "./storage"
    max_uploads_per_spot: int = 3

settings = Settings()