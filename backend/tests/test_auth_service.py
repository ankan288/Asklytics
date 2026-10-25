"""Production test suite for Authentication & Security Services (Password hashing, JWT generation, validation)."""

import pytest
from app.services.auth_service import AuthService


def test_password_hashing_and_verification():
    raw_password = "SecurePassword123!"
    hashed = AuthService.hash_password(raw_password)

    assert ":" in hashed  # salt:hash format
    assert hashed != raw_password

    # Correct password verifies
    assert AuthService.verify_password(raw_password, hashed) is True

    # Wrong password fails
    assert AuthService.verify_password("WrongPassword123!", hashed) is False


def test_jwt_access_and_refresh_token_lifecycle():
    user_id = "12345678-1234-5678-1234-567812345678"
    tokens = AuthService.create_tokens(user_id)

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # Verify access token
    extracted_user = AuthService.verify_access_token(tokens["access_token"])
    assert extracted_user == user_id

    # Verify refresh token
    extracted_refresh = AuthService.verify_refresh_token(tokens["refresh_token"])
    assert extracted_refresh == user_id

    # Cross-type rejection: access token passed as refresh token should be rejected
    assert AuthService.verify_refresh_token(tokens["access_token"]) is None


def test_bearer_token_header_extraction():
    valid_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    token = AuthService.extract_token_from_header(valid_header)
    assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"

    # Missing Bearer prefix
    assert AuthService.extract_token_from_header("Basic 12345") is None
    assert AuthService.extract_token_from_header("") is None
    assert AuthService.extract_token_from_header(None) is None
