"""
Database initialization - Create/upgrade auth tables on app startup.
"""
import sqlite3
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)


def init_auth_tables():
    """
    Create users, sessions, conversations, and conversation_turns tables.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    settings = get_settings()
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()

    try:
        # ─── Users Table ────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        logger.info("✓ users table ready")

        # ─── Sessions Table ─────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                access_token TEXT UNIQUE NOT NULL,
                refresh_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                revoked_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        logger.info("✓ sessions table ready")

        # ─── Conversations Table ────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT,
                datasource_id TEXT DEFAULT 'default',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        logger.info("✓ conversations table ready")

        # ─── Conversation Turns Table (unlimited history!) ──────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_turns (
                turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                turn_number INTEGER,
                user_prompt TEXT NOT NULL,
                sql_generated TEXT,
                charts TEXT,
                insight_summary TEXT,
                data_limitations TEXT,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        logger.info("✓ conversation_turns table ready")

        # ─── Create Indexes for Performance ─────────────────────────────────
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_turns_conversation_id ON conversation_turns(conversation_id)
        """)

        logger.info("✓ all indexes created")

        conn.commit()
        logger.info("✅ Authentication tables initialized successfully")

    except Exception as e:
        logger.error(f"❌ Error initializing auth tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def cleanup_expired_sessions():
    """
    Delete expired sessions older than 7 days.
    Should be called periodically (e.g., via cron or background job).
    """
    settings = get_settings()
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM sessions
            WHERE expires_at < datetime('now')
        """)
        deleted = cursor.rowcount
        conn.commit()
        logger.info(f"✓ Cleaned up {deleted} expired sessions")
        return deleted
    except Exception as e:
        logger.error(f"❌ Error cleaning up sessions: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Can be run directly for testing
    init_auth_tables()
    print("✅ Tables initialized")
