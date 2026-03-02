"""
Spectra — Auth Service Unit Tests
Tests password hashing, verification, and JWT creation/decoding.
"""

from datetime import timedelta

import pytest
from jose import JWTError

from app.services.auth_service import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_bcrypt_hash() -> None:
    """hash_password must return a bcrypt-formatted hash string."""
    hashed = hash_password("securepassword123")
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert len(hashed) > 40


def test_verify_password_correct_returns_true() -> None:
    """verify_password must return True for the correct plain-text password."""
    plain = "mySecretPassword!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_wrong_returns_false() -> None:
    """verify_password must return False for the wrong password."""
    hashed = hash_password("correctpassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_returns_decodable_jwt() -> None:
    """create_access_token must return a JWT whose 'sub' matches the subject."""
    token = create_access_token(subject="user-uuid-1234")
    decoded_subject = decode_token(token)
    assert decoded_subject == "user-uuid-1234"


def test_expired_token_raises_jwt_error() -> None:
    """decode_token must raise JWTError for a token that is already expired."""
    expired_token = create_access_token(
        subject="user-expired",
        expires_delta=timedelta(seconds=-1),  # Already expired
    )
    with pytest.raises(JWTError):
        decode_token(expired_token)
