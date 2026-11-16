"""
User service - Basic user management for SQLite database.
"""
import sqlite3
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional, List
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

    def create_user(self, email: str, hashed_password: str, role: str = "user") -> str:
        """
        Create a new user with specified role.
        """
        user_id = str(uuid.uuid4())

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, email, hashed_password, created_at, role)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, email.lower().strip(), hashed_password, datetime.utcnow().isoformat(), role))
            conn.commit()
            logger.info(f"✓ User created: {user_id} with role {role}")
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
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
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

    def list_users(self, limit: int = 50) -> List[Dict]:
        """List registered users without sensitive password hashes."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, email, role, created_at, last_login, is_active
                FROM users
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
        finally:
            conn.close()

    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update user role (e.g. 'user' or 'admin')."""
        if new_role not in ["user", "admin"]:
            raise ValueError("Role must be 'user' or 'admin'")

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET role = ? WHERE user_id = ?
            """, (new_role, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def create_session(self, user_id: str) -> Dict[str, str]:
        """Create session with JWT tokens."""
        try:
            tokens = AuthService.create_tokens(user_id)

            conn = self._get_connection()
            cursor = conn.cursor()

            session_id = str(uuid.uuid4())
            expires_at = datetime.utcnow()
            expires_at = expires_at.replace(day=expires_at.day + 7)

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
