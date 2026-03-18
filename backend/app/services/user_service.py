"""
User service - Basic user management for SQLite database.
Minimal implementation for auth router compatibility.
"""
import sqlite3
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional
from app.config import get_settings
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """Handles user CRUD operations with SQLite database."""

    def __init__(self):
        self.settings = get_settings()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.settings.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def create_user(self, email: str, hashed_password: str) -> str:
        """
        Create a new user.

        Args:
            email: User email
            hashed_password: Already hashed password

        Returns:
            user_id: UUID string

        Raises:
            ValueError: If email already exists
        """
        user_id = str(uuid.uuid4())

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, email, hashed_password, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, email, hashed_password, datetime.utcnow().isoformat()))
            conn.commit()
            logger.info(f"✓ User created: {user_id}")
            return user_id
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None
        finally:
            conn.close()

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None
        finally:
            conn.close()

    def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE user_id = ?
            """, (datetime.utcnow().isoformat(), user_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
        finally:
            conn.close()

    def create_session(self, user_id: str) -> Dict[str, str]:
        """
        Create session with JWT tokens.

        Args:
            user_id: UUID of user

        Returns:
            Dict with access_token, refresh_token, token_type, expires_in
        """
        try:
            # Generate JWT tokens using AuthService
            tokens = AuthService.create_tokens(user_id)

            # Store session in database
            conn = self._get_connection()
            cursor = conn.cursor()

            session_id = str(uuid.uuid4())
            expires_at = datetime.utcnow()
            expires_at = expires_at.replace(day=expires_at.day + 7)  # 7 days from now

            cursor.execute("""
                INSERT INTO sessions (session_id, user_id, access_token, refresh_token, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                tokens["access_token"],
                tokens["refresh_token"],
                expires_at.isoformat()
            ))
            conn.commit()
            conn.close()

            logger.debug(f"✓ Session created for user: {user_id}")
            return tokens

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise ValueError("Failed to create session")