"""
Spectra — Auth Service
Handles password hashing, JWT creation, and token decoding.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password utilities ─────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# ── JWT utilities ──────────────────────────────────────────────────────────────

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The unique identifier to embed (usually user ID or username).
        expires_delta: Custom expiry window; falls back to settings.jwt_expire_minutes.

    Returns:
        Encoded JWT string.
    """
    delta = expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    expire = datetime.now(timezone.utc) + delta
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str:
    """
    Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.

    Returns:
        The 'sub' (subject) claim from the token.

    Raises:
        JWTError: If the token is invalid, expired, or malformed.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    subject: Optional[str] = payload.get("sub")
    if subject is None:
        raise JWTError("Token payload missing 'sub' claim.")
    return subject
