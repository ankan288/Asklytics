"""SQL execution — SELECT only, injection-safe."""
import sqlite3, re, logging
from typing import Any
from app.database.connection import get_file_connection, get_inmemory
from app.config import get_settings

logger = logging.getLogger(__name__)
_FORBIDDEN = re.compile(r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|ATTACH|DETACH|PRAGMA)\b", re.IGNORECASE)


def execute_query(sql: str, datasource_id: str = "default") -> list[dict[str, Any]]:
    sql = sql.strip().rstrip(";")
    if sql.split()[0].upper() != "SELECT":
        raise PermissionError("Only SELECT statements are allowed.")
    if _FORBIDDEN.search(sql):
        raise PermissionError("Statement contains forbidden keywords.")

    if datasource_id == "default":
        conn = get_file_connection(get_settings().db_path)
        should_close = True
    else:
        conn = get_inmemory(datasource_id)
        if conn is None:
            raise ValueError(f"Unknown datasource: {datasource_id}")
        should_close = False

    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError as e:
        raise ValueError(f"SQL error: {e}")
    finally:
        if should_close:
            conn.close()
