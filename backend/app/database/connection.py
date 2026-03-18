import sqlite3
from typing import Optional

# Registry for in-memory connections (uploaded CSVs) keyed by datasource_id
_inmemory: dict[str, sqlite3.Connection] = {}


def get_file_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def register_inmemory(datasource_id: str, conn: sqlite3.Connection) -> None:
    _inmemory[datasource_id] = conn


def get_inmemory(datasource_id: str) -> Optional[sqlite3.Connection]:
    return _inmemory.get(datasource_id)


def list_datasources() -> list[str]:
    return ["default"] + list(_inmemory.keys())
