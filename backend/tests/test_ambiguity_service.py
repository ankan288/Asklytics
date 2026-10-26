import pytest
from app.services.ambiguity_service import check_ambiguity


def test_detects_ambiguous_best_category():
    result = check_ambiguity("Show me the best category")
    assert result is not None
    assert result["is_ambiguous"] is True
    assert "best category" in result["matched_term"].lower()
    assert len(result["options"]) >= 3
    assert any("revenue" in opt["subtext"].lower() for opt in result["options"])


def test_ignores_specified_best_category():
    # If the user specifies the evaluation criteria, it is unambiguous
    result = check_ambiguity("Show me the best category by total revenue")
    assert result is None


def test_detects_ambiguous_top_region():
    result = check_ambiguity("Who is the leading region?")
    assert result is not None
    assert result["is_ambiguous"] is True
    assert "leading region" in result["matched_term"].lower()


def test_detects_recent_sales_ambiguity():
    result = check_ambiguity("Show recent sales")
    assert result is not None
    assert result["is_ambiguous"] is True
    assert "recent" in result["matched_term"].lower()


def test_unambiguous_specific_query_passes_clean():
    result = check_ambiguity("SELECT SUM(total_revenue) FROM amazon_sales WHERE order_date >= '2023-01-01'")
    assert result is None
