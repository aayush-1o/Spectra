"""
Spectra — Application Configuration
Reads settings from environment variables / .env file via Pydantic Settings.

Phase 7 additions:
  - CORS_ORIGINS: comma-separated env var overrides hardcoded list in production
  - LOG_LEVEL, DEBUG: control log verbosity per environment
  - ALLOW_DOCS: disables /docs and /redoc in production
  - Startup safety check: crashes if JWT secret is default in production
  - FRONTEND_URL: used to build production CORS allow-list
"""

import logging
import sys
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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

    # ── Neo4j ──────────────────────────────────────────────────────────────────
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

    # Phase 7: Production behaviour flags
    # LOG_LEVEL controls uvicorn + app log level (DEBUG | INFO | WARNING | ERROR)
    log_level: str = "INFO"
    # DEBUG=true enables SQLAlchemy echo, detailed error tracebacks in responses
    debug: bool = False
    # ALLOW_DOCS=false hides /docs and /redoc in production
    allow_docs: bool = True
    # FRONTEND_URL: production frontend URL (appended to CORS allow-list)
    frontend_url: str = ""
    # CORS_ORIGINS: optional comma-separated override (takes precedence over all)
    cors_origins_override: str = ""

    # ── Derived properties ─────────────────────────────────────────────────────

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origins(self) -> List[str]:
        """
        Build the CORS allow-list.

        Priority:
          1. CORS_ORIGINS_OVERRIDE — explicit comma-separated list (highest priority)
          2. Default dev origins + FRONTEND_URL if set
        """
        if self.cors_origins_override:
            return [o.strip() for o in self.cors_origins_override.split(",") if o.strip()]

        origins = ["http://localhost:5173", "http://localhost:3000"]
        if self.frontend_url:
            origins.append(self.frontend_url.rstrip("/"))
        return origins

    def validate_production(self) -> None:
        """
        Safety guard — called once at startup.
        Crashes with a descriptive error if the app is misconfigured for production.
        """
        if not self.is_production:
            return

        errors: list[str] = []

        if self.jwt_secret_key in ("CHANGE_ME_IN_PRODUCTION", "changeme", "secret"):
            errors.append(
                "JWT_SECRET_KEY is set to a placeholder. "
                "Generate a real key: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        if not self.frontend_url and not self.cors_origins_override:
            errors.append(
                "In production, set FRONTEND_URL=https://your-frontend.vercel.app "
                "OR CORS_ORIGINS_OVERRIDE=https://your-frontend.vercel.app to restrict CORS."
            )

        if errors:
            for err in errors:
                logger.critical("PRODUCTION CONFIG ERROR: %s", err)
            sys.exit(
                "\n\n❌ STARTUP ABORTED — production configuration is invalid.\n"
                + "\n".join(f"  • {e}" for e in errors)
                + "\n\nFix the above issues and restart.\n"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
