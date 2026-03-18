"""Schema introspection — reads SQLite PRAGMA and formats a compact string for Gemini."""
import sqlite3, json, logging
from app.database.connection import get_file_connection, get_inmemory
from app.config import get_settings

logger = logging.getLogger(__name__)


def _get_conn(datasource_id: str) -> tuple:
    if datasource_id == "default":
        return get_file_connection(get_settings().db_path), True
    conn = get_inmemory(datasource_id)
    if conn is None:
        raise ValueError(f"Unknown datasource: {datasource_id}")
    return conn, False


def get_compact_schema(datasource_id: str = "default") -> str:
    conn, should_close = _get_conn(datasource_id)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r["name"] for r in cur.fetchall()]
        parts = []
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            cols = cur.fetchall()
            col_defs = ", ".join(f"{c['name']} {c['type']}" for c in cols)
            parts.append(f"TABLE {table}({col_defs})")

            # Total row count — helps the LLM understand data scale
            cur.execute(f"SELECT COUNT(*) as n FROM \"{table}\"")
            total_rows = cur.fetchone()["n"]
            parts.append(f"TOTAL ROWS: {total_rows}")

            # Per-column statistics — prevents hallucinated column values
            col_stats = []
            for c in cols:
                name, ctype = c["name"], (c["type"] or "").upper()
                try:
                    if any(t in ctype for t in ("INT", "REAL", "NUM", "FLOAT", "DOUBLE")):
                        cur.execute(f'SELECT MIN("{name}"), MAX("{name}") FROM "{table}"')
                        row = cur.fetchone()
                        col_stats.append(f'  {name}: range [{row[0]}, {row[1]}]')
                    else:
                        cur.execute(f'SELECT COUNT(DISTINCT "{name}") FROM "{table}"')
                        dc = cur.fetchone()[0]
                        if dc <= 12:
                            cur.execute(f'SELECT DISTINCT "{name}" FROM "{table}" LIMIT 12')
                            vals = [r[0] for r in cur.fetchall()]
                            col_stats.append(f'  {name}: {dc} distinct values = {vals}')
                        else:
                            col_stats.append(f'  {name}: {dc} distinct values')
                except Exception:
                    pass  # skip unsupported column types silently
            if col_stats:
                parts.append("COLUMN STATS:\n" + "\n".join(col_stats))

            # 2 sample rows for concrete value context
            cur.execute(f'SELECT * FROM "{table}" LIMIT 2')
            rows = [dict(r) for r in cur.fetchall()]
            parts.append(f"SAMPLE ROWS:\n{json.dumps(rows, indent=2, default=str)}")
        return "\n".join(parts)
    finally:
        if should_close:
            conn.close()
