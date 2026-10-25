"""Production test suite for CSV Ingestion Service (schema inference, column sanitization, in-memory SQLite registration)."""

import asyncio
import pytest
from app.services import csv_service
from app.database.connection import get_inmemory


def test_process_valid_csv():
    csv_data = b"product,revenue,units_sold\nLaptop,1200.50,5\nMouse,25.00,40\nKeyboard,45.00,15"
    result = asyncio.run(csv_service.process_csv(csv_data, "sales.csv"))

    assert "datasource_id" in result
    assert result["table_name"] == "uploaded_data"
    assert result["row_count"] == 3
    assert "product" in result["schema"]
    assert "revenue" in result["schema"]

    # Verify queryability in in-memory SQLite
    conn = get_inmemory(result["datasource_id"])
    assert conn is not None
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM uploaded_data")
    assert cur.fetchone()[0] == 3


def test_sanitizes_complex_column_names():
    csv_data = b"Product Name (Global),Order Total [USD],Customer & Region\nItem A,100,US"
    result = asyncio.run(csv_service.process_csv(csv_data, "complex.csv"))

    schema_keys = list(result["schema"].keys())
    # All non-alphanumeric characters should be replaced with underscores
    for key in schema_keys:
        assert "(" not in key
        assert ")" not in key
        assert "[" not in key
        assert "]" not in key
        assert "&" not in key
        assert " " not in key


def test_rejects_empty_csv():
    csv_data = b""
    with pytest.raises(ValueError):
        asyncio.run(csv_service.process_csv(csv_data, "empty.csv"))


def test_strips_html_pre_tags():
    csv_data = b"<pre>category,sales\nBooks,350\nGames,1200</pre>"
    result = asyncio.run(csv_service.process_csv(csv_data, "wrapped.csv"))
    assert result["row_count"] == 2
    assert "category" in result["schema"]
