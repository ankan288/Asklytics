import pytest
from app.services.chart_validator import validate_and_sanitize_charts


def test_pie_chart_with_more_than_7_rows_auto_converts_to_bar():
    # 10 categories
    rows = [{"category": f"Cat_{i}", "revenue": 100 * i} for i in range(10)]
    raw_charts = [{
        "id": "c1",
        "type": "pie",
        "title": "Revenue by Category",
        "x_key": "category",
        "y_keys": ["revenue"],
    }]
    sanitized, corrections = validate_and_sanitize_charts(raw_charts, rows)
    assert len(sanitized) == 1
    assert sanitized[0]["type"] == "bar"
    assert any("Auto-converted pie chart" in c for c in corrections)


def test_pie_chart_with_5_rows_retains_pie_type():
    rows = [{"category": f"Cat_{i}", "revenue": 100 * i} for i in range(5)]
    raw_charts = [{
        "id": "c1",
        "type": "pie",
        "title": "Revenue by Category",
        "x_key": "category",
        "y_keys": ["revenue"],
    }]
    sanitized, corrections = validate_and_sanitize_charts(raw_charts, rows)
    assert sanitized[0]["type"] == "pie"
    assert len(corrections) == 0


def test_line_chart_with_categorical_x_axis_auto_converts_to_bar():
    rows = [
        {"region": "North", "sales": 500},
        {"region": "South", "sales": 400},
        {"region": "East", "sales": 300},
    ]
    raw_charts = [{
        "id": "c2",
        "type": "line",
        "title": "Sales by Region",
        "x_key": "region",
        "y_keys": ["sales"],
    }]
    sanitized, corrections = validate_and_sanitize_charts(raw_charts, rows)
    assert sanitized[0]["type"] == "bar"
    assert any("categorical data rather than a continuous" in c for c in corrections)


def test_line_chart_with_temporal_x_axis_retains_line_type():
    rows = [
        {"order_date": "2023-01-01", "sales": 100},
        {"order_date": "2023-02-01", "sales": 200},
        {"order_date": "2023-03-01", "sales": 300},
    ]
    raw_charts = [{
        "id": "c3",
        "type": "line",
        "title": "Monthly Sales Trend",
        "x_key": "order_date",
        "y_keys": ["sales"],
    }]
    sanitized, corrections = validate_and_sanitize_charts(raw_charts, rows)
    assert sanitized[0]["type"] == "line"
    assert len(corrections) == 0


def test_kpi_card_extracts_single_scalar():
    rows = [
        {"total_revenue": 12500.50},
        {"total_revenue": 8400.00},
    ]
    raw_charts = [{
        "id": "c4",
        "type": "kpi",
        "title": "Total Revenue",
        "x_key": None,
        "y_keys": ["total_revenue"],
    }]
    sanitized, _ = validate_and_sanitize_charts(raw_charts, rows)
    assert sanitized[0]["data"] == [{"value": 12500.50}]
