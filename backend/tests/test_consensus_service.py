import pytest
from app.services.consensus_service import compare_sql_semantics


def test_identical_sql_yields_full_consensus():
    sql1 = "SELECT category, SUM(total_revenue) FROM amazon_sales GROUP BY category;"
    sql2 = "SELECT category, SUM(total_revenue) AS rev FROM amazon_sales GROUP BY category ORDER BY rev DESC;"
    res = compare_sql_semantics(sql1, sql2)
    assert res.agreement_score >= 0.80
    assert res.status == "CONSENSUS_REACHED"
    assert len(res.differences) == 0


def test_aggregation_mismatch_flags_divergence():
    sql1 = "SELECT category, SUM(total_revenue) FROM amazon_sales GROUP BY category;"
    sql2 = "SELECT category, COUNT(order_id) FROM amazon_sales GROUP BY category;"
    res = compare_sql_semantics(sql1, sql2)
    assert res.status == "DIVERGENCE_DETECTED"
    assert any("Aggregation mismatch" in d for d in res.differences)


def test_single_model_fallback():
    sql1 = "SELECT * FROM amazon_sales LIMIT 10;"
    res = compare_sql_semantics(sql1, None)
    assert res.status == "SINGLE_MODEL"
    assert res.agreement_score == 1.0
