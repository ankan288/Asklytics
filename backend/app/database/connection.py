import sqlite3
import os
from typing import Optional, Union, Any
from contextlib import contextmanager

# For PostgreSQL support in production
try:
    import psycopg2
    import psycopg2.extras
    from psycopg2.pool import SimpleConnectionPool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from app.config import get_settings

# Registry for in-memory connections (uploaded CSVs) - will be replaced with Supabase Storage
_inmemory: dict[str, sqlite3.Connection] = {}

# PostgreSQL connection pool for production
_postgres_pool: Optional[SimpleConnectionPool] = None

def init_postgres_pool():
    """Initialize PostgreSQL connection pool for production"""
    global _postgres_pool
    settings = get_settings()

    if not settings.postgres_url or not POSTGRES_AVAILABLE:
        return

    try:
        _postgres_pool = SimpleConnectionPool(
            1, 10,  # min=1, max=10 connections
            settings.postgres_url
        )
        print("✅ PostgreSQL connection pool initialized")
    except Exception as e:
        print(f"❌ Failed to initialize PostgreSQL pool: {e}")
        _postgres_pool = None

@contextmanager
def get_database_connection():
    """
    Get appropriate database connection based on environment
    - Production: PostgreSQL (Supabase)
    - Development: SQLite (local file)
    """
    settings = get_settings()

    if settings.use_postgres and _postgres_pool:
        # Production PostgreSQL connection
        conn = _postgres_pool.getconn()
        try:
            yield conn
        finally:
            _postgres_pool.putconn(conn)
    else:
        # Development SQLite connection
        conn = sqlite3.connect(settings.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

def get_file_connection(db_path: str) -> sqlite3.Connection:
    """Legacy SQLite connection for local development"""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_connection():
    """Get PostgreSQL connection for production queries"""
    settings = get_settings()
    if not settings.postgres_url or not POSTGRES_AVAILABLE:
        raise Exception("PostgreSQL not configured or psycopg2 not installed")

    conn = psycopg2.connect(settings.postgres_url)
    conn.autocommit = True
    return conn

# Legacy in-memory functions (will be replaced with Supabase Storage)
def register_inmemory(datasource_id: str, conn: sqlite3.Connection) -> None:
    """Register in-memory SQLite connection (temporary - will migrate to Supabase Storage)"""
    _inmemory[datasource_id] = conn

def get_inmemory(datasource_id: str) -> Optional[sqlite3.Connection]:
    """Get in-memory SQLite connection (temporary - will migrate to Supabase Storage)"""
    return _inmemory.get(datasource_id)

def list_datasources() -> list[str]:
    """List available datasources"""
    return ["default"] + list(_inmemory.keys())

def execute_query(query: str, datasource_id: str = "default") -> list[dict]:
    """
    Execute SQL query against appropriate database
    - default: Main database (SQLite dev / PostgreSQL prod)
    - other: In-memory CSV uploads (will migrate to Supabase Storage)
    """
    if datasource_id == "default":
        # Query main database
        with get_database_connection() as conn:
            settings = get_settings()

            if settings.use_postgres:
                # PostgreSQL query
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cursor.execute(query)
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                # SQLite query
                cursor = conn.execute(query)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        # Query in-memory CSV (legacy - will migrate)
        conn = get_inmemory(datasource_id)
        if not conn:
            raise Exception(f"Datasource {datasource_id} not found")

        cursor = conn.execute(query)
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
