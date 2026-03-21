"""
Asklytics: Authentication service - JWT token generation/validation
and integration with Supabase Auth.

Note: For signup/login, use Supabase Auth API directly via frontend.
This service handles JWT validation for API authentication.
"""
import jwt
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class AuthService:
    """Handles JWT tokens and password validation."""

    # ─── Password Hashing ───────────────────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 with salt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string (salt:hash format)
        """
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((salt + password).encode())
        return f"{salt}:{hash_obj.hexdigest()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored hash (salt:hash format)

        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, stored_hash = hashed_password.split(":")
            hash_obj = hashlib.sha256((salt + password).encode())
            return hash_obj.hexdigest() == stored_hash
        except (ValueError, AttributeError):
            return False

    # ─── JWT Token Generation ──────────────────────────────────────────────

    @staticmethod
    def create_access_token(user_id: str) -> Tuple[str, dict]:
        """
        Create JWT access token (short-lived, 1 hour).

        Args:
            user_id: UUID of user (as string)

        Returns:
            Tuple of (token_string, token_info_dict)
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

        payload = {
            "sub": user_id,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        try:
            token = jwt.encode(
                payload,
                settings.supabase_jwt_secret,
                algorithm=settings.jwt_algorithm
            )
            logger.debug(f"Created access token for user {user_id}")
            return token, {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": settings.jwt_access_token_expire_minutes * 60  # seconds
            }
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    @staticmethod
    def create_refresh_token(user_id: str) -> Tuple[str, dict]:
        """
        Create JWT refresh token (long-lived, 7 days).

        Args:
            user_id: UUID of user (as string)

        Returns:
            Tuple of (token_string, token_info_dict)
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        try:
            token = jwt.encode(
                payload,
                settings.supabase_jwt_secret,
                algorithm=settings.jwt_algorithm
            )
            logger.debug(f"Created refresh token for user {user_id}")
            return token, {
                "refresh_token": token,
                "expires_in": settings.jwt_refresh_token_expire_days * 86400  # seconds
            }
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise

    @staticmethod
    def create_tokens(user_id: str) -> Dict[str, str]:
        """
        Generate JWT access token (1 hour) and refresh token (7 days).

        Args:
            user_id: The user's UUID

        Returns:
            {
                "access_token": "eyJ0eXAi...",
                "refresh_token": "eyJ0eXAi...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        """
        access_token, _ = AuthService.create_access_token(user_id)
        refresh_token, _ = AuthService.create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600  # 1 hour in seconds (for access token)
        }

    # ─── Token Verification ────────────────────────────────────────────────

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[str]:
        """
        Verify JWT token and return user_id.

        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")

        Returns:
            user_id (UUID as string) if valid, None if invalid/expired
        """
        settings = get_settings()
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )

            # Verify token type (Supabase JWTs do not have a 'type' claim)
            token_type_from_payload = payload.get("type")
            if token_type_from_payload and token_type_from_payload != token_type:
                logger.warning(f"Invalid token type: expected {token_type}, got {token_type_from_payload}")
                return None

            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token missing 'sub' (user_id)")
                return None

            return user_id

        except jwt.ExpiredSignatureError:
            logger.debug(f"Token expired: {token_type}")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    @staticmethod
    def verify_access_token(token: str) -> Optional[str]:
        """Verify access token and return user_id."""
        return AuthService.verify_token(token, token_type="access")

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[str]:
        """Verify refresh token and return user_id."""
        return AuthService.verify_token(token, token_type="refresh")

    @staticmethod
    def decode_token(token: str) -> Dict:
        """
        Decode JWT token without verification (for debugging only).

        Args:
            token: JWT token string

        Returns:
            Decoded payload dictionary
        """
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return {}

    # ─── Token Refresh ─────────────────────────────────────────────────────

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Generate new access token using valid refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            {
                "access_token": "new_token",
                "token_type": "bearer",
                "expires_in": 3600
            }
            or None if refresh_token invalid/expired
        """
        user_id = AuthService.verify_refresh_token(refresh_token)

        if not user_id:
            logger.warning("Invalid or expired refresh token")
            return None

        access_token, token_info = AuthService.create_access_token(user_id)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600  # 1 hour in seconds
        }

    # ─── Token Utilities ───────────────────────────────────────────────────

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Supabase enforces password requirements, but we validate
        client-side for better UX.

        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number

        Args:
            password: Password string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        return True, ""

    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """
        Extract JWT token from Authorization header.

        Expected format: "Bearer <token>"

        Args:
            auth_header: Authorization header value

        Returns:
            Token string or None if invalid format
        """
        if not auth_header:
            return None

        parts = auth_header.split(" ", 1)

        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.debug(f"Invalid auth header format")
            return None

        return parts[1]

    @staticmethod
    def get_token_expiry_info(token: str) -> Optional[dict]:
        """
        Get expiry information for a token.

        Args:
            token: JWT token

        Returns:
            Dict with expiry details, or None if token invalid
        """
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = unverified.get("exp")

            if not exp_timestamp:
                return None

            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)

            return {
                "expires_at": exp_datetime.isoformat(),
                "expires_in_seconds": int((exp_datetime - now).total_seconds()),
                "is_expired": now > exp_datetime
            }
        except Exception as e:
            logger.debug(f"Error getting token expiry info: {e}")
            return None

    @staticmethod
    def should_refresh_token(token: str) -> bool:
        """
        Check if access token should be refreshed (within 5 minutes of expiry).

        Args:
            token: JWT access token

        Returns:
            True if token should be refreshed
        """
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            exp_timestamp = unverified.get("exp")

            if not exp_timestamp:
                return True

            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)

            # Refresh if less than 5 minutes until expiry
            refresh_threshold = timedelta(minutes=5)
            return (exp_datetime - now) < refresh_threshold

        except Exception as e:
            logger.debug(f"Error checking token expiry: {e}")
            return True
