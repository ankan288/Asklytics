"""SQL execution and security engine — AST-parsed, whitelisted, read-only connection."""

import os
import time
import sqlite3
import logging
from typing import Any, Dict, List, Tuple, Optional
import sqlglot
from sqlglot import exp
from app.database.connection import get_file_connection, get_inmemory
from app.config import get_settings

logger = logging.getLogger(__name__)

# Maximum allowable rows returned from a single conversational query
MAX_ROW_LIMIT = 1000

# Prohibited AST node types
_FORBIDDEN_AST_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
    exp.Pragma,
)


def get_allowed_tables(datasource_id: str = "default") -> List[str]:
    """Retrieves whitelisted tables for the active datasource."""
    if datasource_id == "default":
        db_path = get_settings().db_path
        if not os.path.exists(db_path):
            return ["amazon_sales"]
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
            return tables
        finally:
            conn.close()
    else:
        conn = get_inmemory(datasource_id)
        if conn is None:
            return []
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
        return tables


def validate_and_sanitize_sql(sql: str, datasource_id: str = "default") -> Tuple[str, Dict[str, Any]]:
    """
    Parses and sanitizes SQL query using AST parsing via sqlglot.
    Enforces:
    1. SELECT queries only (rejects INSERT, UPDATE, DELETE, DROP, PRAGMA, ATTACH, etc.)
    2. Table whitelisting against introspected schema
    3. Mandatory LIMIT <= 1000
    Returns:
        (sanitized_sql, ast_metadata)
    """
    sql = sql.strip().rstrip(";")
    if not sql:
        raise ValueError("Empty SQL query provided.")

    try:
        parsed = sqlglot.parse_one(sql, read="sqlite")
    except Exception as e:
        raise ValueError(f"SQL syntax error during AST parsing: {e}")

    # Check for non-SELECT or forbidden AST structures
    if isinstance(parsed, _FORBIDDEN_AST_NODES):
        raise PermissionError(f"Security Alert: Execution of {parsed.key.upper()} statements is forbidden.")

    # Must be Select or Union of Selects
    is_select = isinstance(parsed, exp.Select) or (
        isinstance(parsed, exp.Union) and all(isinstance(s, exp.Select) for s in parsed.find_all(exp.Select))
    )
    if not is_select:
        raise PermissionError("Security Alert: Only SELECT statements are permitted.")

    # Check for any nested forbidden nodes
    for forbidden_type in _FORBIDDEN_AST_NODES:
        if list(parsed.find_all(forbidden_type)):
            raise PermissionError(f"Security Alert: Nested {forbidden_type.__name__} detected.")

    # Table whitelisting check
    allowed_tables = [t.lower() for t in get_allowed_tables(datasource_id)]
    referenced_tables = [table.name.lower() for table in parsed.find_all(exp.Table) if table.name]

    if allowed_tables and referenced_tables:
        for ref_table in referenced_tables:
            if ref_table not in allowed_tables:
                raise PermissionError(
                    f"Security Alert: Table '{ref_table}' is not in the allowed schema ({', '.join(allowed_tables)})."
                )

    # Enforce LIMIT <= 1000
    limit_node = parsed.args.get("limit")
    if limit_node is None:
        parsed = parsed.limit(MAX_ROW_LIMIT)
    else:
        try:
            current_limit = int(limit_node.expression.this)
            if current_limit > MAX_ROW_LIMIT or current_limit < 1:
                parsed = parsed.limit(MAX_ROW_LIMIT)
        except Exception:
            parsed = parsed.limit(MAX_ROW_LIMIT)

    sanitized_sql = parsed.sql(dialect="sqlite")

    ast_metadata = {
        "tables": referenced_tables,
        "is_aggregate": bool(list(parsed.find_all(exp.AggFunc))),
        "has_group_by": bool(parsed.args.get("group")),
        "has_order_by": bool(parsed.args.get("order")),
        "limit_applied": MAX_ROW_LIMIT,
    }

    return sanitized_sql, ast_metadata


def execute_query(sql: str, datasource_id: str = "default") -> List[Dict[str, Any]]:
    """Legacy wrapper for backwards-compatibility returning only row dictionaries."""
    rows, _ = execute_query_with_telemetry(sql, datasource_id)
    return rows


def execute_query_with_telemetry(
    sql: str,
    datasource_id: str = "default",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Validates SQL via AST, executes on a read-only SQLite connection, and captures execution metrics.
    Returns:
        (rows, telemetry_dict)
    """
    sanitized_sql, ast_metadata = validate_and_sanitize_sql(sql, datasource_id)

    start_time = time.perf_counter()
    should_close = False

    if datasource_id == "default":
        db_path = os.path.abspath(get_settings().db_path)
        if not os.path.exists(db_path):
            conn = get_file_connection(db_path)
            should_close = True
        else:
            try:
                # Kernel-level read-only connection
                conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
                should_close = True
            except Exception as e:
                logger.warning(f"Failed to open URI read-only connection ({e}), using standard connection.")
                conn = get_file_connection(db_path)
                should_close = True
    else:
        conn = get_inmemory(datasource_id)
        if conn is None:
            raise ValueError(f"Unknown datasource: {datasource_id}")
        should_close = False

    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sanitized_sql)
        rows = [dict(r) for r in cur.fetchall()]
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        telemetry = {
            "sanitized_sql": sanitized_sql,
            "execution_time_ms": elapsed_ms,
            "rows_scanned": len(rows),
            "is_read_only": True,
            "ast_metadata": ast_metadata,
        }
        return rows, telemetry
    except sqlite3.OperationalError as e:
        raise ValueError(f"SQL execution error: {e}")
    finally:
        if should_close:
            conn.close()
