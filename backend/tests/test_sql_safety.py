"""Unit tests for AST-level SQL validation and injection defense (P2SQL benchmark tests)."""

import pytest
from app.services.sql_service import validate_and_sanitize_sql, execute_query


def test_valid_select_query():
    sql = "SELECT product_category, SUM(total_revenue) AS rev FROM amazon_sales GROUP BY product_category"
    sanitized, meta = validate_and_sanitize_sql(sql, "default")
    assert "SELECT" in sanitized
    assert "LIMIT 1000" in sanitized
    assert "amazon_sales" in meta["tables"]
    assert meta["has_group_by"] is True


def test_blocks_drop_table():
    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("DROP TABLE amazon_sales", "default")


def test_blocks_delete_from():
    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("DELETE FROM amazon_sales WHERE order_id = 1", "default")


def test_blocks_update():
    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("UPDATE amazon_sales SET total_revenue = 9999", "default")


def test_blocks_insert():
    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("INSERT INTO amazon_sales (order_id) VALUES (999)", "default")


def test_blocks_pragma():
    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("PRAGMA table_info(amazon_sales)", "default")


def test_blocks_nested_malicious_subquery():
    with pytest.raises(Exception):
        validate_and_sanitize_sql("SELECT * FROM amazon_sales; DROP TABLE amazon_sales;", "default")


def test_enforces_limit_clamping():
    sql = "SELECT * FROM amazon_sales LIMIT 50000"
    sanitized, _ = validate_and_sanitize_sql(sql, "default")
    assert "LIMIT 1000" in sanitized


def test_preserves_smaller_limit():
    sql = "SELECT * FROM amazon_sales LIMIT 5"
    sanitized, _ = validate_and_sanitize_sql(sql, "default")
    assert "LIMIT 5" in sanitized


def test_allows_valid_with_cte_query():
    sql = (
        "WITH regional_summary AS ("
        "  SELECT product_category, SUM(total_revenue) AS rev FROM amazon_sales GROUP BY product_category"
        ") SELECT * FROM regional_summary"
    )
    sanitized, meta = validate_and_sanitize_sql(sql, "default")
    assert "WITH" in sanitized
    assert meta["has_with_cte"] is True


def test_blocks_forbidden_functions():
    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("SELECT load_extension('exploit.so') FROM amazon_sales", "default")

    with pytest.raises(PermissionError):
        validate_and_sanitize_sql("SELECT randomblob(1000000000) FROM amazon_sales", "default")


def test_blocks_unwhitelisted_column():
    with pytest.raises(PermissionError) as exc:
        validate_and_sanitize_sql("SELECT non_existent_secret_column FROM amazon_sales", "default")
    assert "does not exist in allowed tables" in str(exc.value)
