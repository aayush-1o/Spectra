"""
Spectra — Application Configuration
Reads settings from environment variables / .env file via Pydantic Settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://spectra:spectra@localhost:5432/spectra"
    )

    # ── Neo4j (Phase 3 — not used yet) ────────────────────────────────────────
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "spectra123"

    # ── Redis ──────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379"

    # ── JWT ────────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # ── App ────────────────────────────────────────────────────────────────────
    environment: str = "development"

    @property
    def cors_origins(self) -> List[str]:
        origins = ["http://localhost:5173", "http://localhost:3000"]
        if self.environment == "production":
            # Add Vercel production domain here once deployed
            origins.append("https://spectra.vercel.app")
        return origins

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
