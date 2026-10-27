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


def test_user_test_a_what_is_the_best_product_category():
    """User Test A: 'What is the best product category?' must trigger clarification chips."""
    result = check_ambiguity("What is the best product category?")
    assert result is not None
    assert result["is_ambiguous"] is True
    assert "How would you like to evaluate the 'best' category?" in result["question"]
    assert len(result["options"]) == 3
    # Check that option refined prompts are unambiguous
    for opt in result["options"]:
        assert check_ambiguity(opt["refined_prompt"]) is None


def test_user_test_b_show_me_recent_sales():
    """User Test B: 'Show me recent sales.' must trigger timeframe clarification chips."""
    result = check_ambiguity("Show me recent sales.")
    assert result is not None
    assert result["is_ambiguous"] is True
    assert "Which timeframe do you mean by 'recent'?" in result["question"]
    assert len(result["options"]) == 3
    for opt in result["options"]:
        assert check_ambiguity(opt["refined_prompt"]) is None


def test_user_test_c_specific_year_query_passes_without_ambiguity():
    """User Test C: 'Calculate total revenue by product category for 2022.' has explicit metric & year."""
    result = check_ambiguity("Calculate total revenue by product category for 2022.")
    assert result is None


def test_unambiguous_specific_query_passes_clean():
    result = check_ambiguity("SELECT SUM(total_revenue) FROM amazon_sales WHERE order_date >= '2023-01-01'")
    assert result is None
