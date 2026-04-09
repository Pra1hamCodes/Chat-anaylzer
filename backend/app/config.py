"""Environment-driven settings (pydantic v1-compatible)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings  # type: ignore
    _V2 = True
except ImportError:  # pydantic v1
    from pydantic import BaseSettings  # type: ignore
    _V2 = False

from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "WhatsApp Analyzer"
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./data/analyzer.db"
    upload_dir: Path = Path("./data/uploads")
    session_ttl_hours: int = 24
    max_upload_size_mb: int = 50

    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    rate_limit_uploads_per_hour: int = 10
    rate_limit_api_per_minute: int = 100

    enable_bertopic: bool = False
    anonymize_usernames: bool = False

    if _V2:  # pragma: no cover
        from pydantic_settings import SettingsConfigDict  # type: ignore
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    else:
        class Config:
            env_file = ".env"
            extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.upload_dir.mkdir(parents=True, exist_ok=True)
    Path("./data").mkdir(parents=True, exist_ok=True)
    return s
