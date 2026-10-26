"""Unit tests for Claim-Level Insight Verification (ConDABench & InsightLens benchmarks)."""

import pytest
from app.services.claim_verifier import verify_insight


def test_verifies_exact_match():
    rows = [
        {"category": "Electronics", "revenue": 145200.0},
        {"category": "Fashion", "revenue": 98700.0},
    ]
    insight = "Electronics generated the highest revenue at $145.2k."
    result = verify_insight(insight, rows)

    assert result["verified"] is True
    assert result["verification_rate"] >= 0.70
    assert result["claims_verified"] >= 1


def test_exact_cents_matching_and_no_loose_tolerance_cross_attribution():
    """
    Validates that exact financial figures ($66.48) match the exact row (Beauty: 66.48)
    and are NOT falsely matched to nearby rows (Sports: 67.49) via loose tolerance.
    """
    rows = [
        {"product_category": "Electronics", "total_revenue": 1132.46},
        {"product_category": "Fashion", "total_revenue": 276.95},
        {"product_category": "Home & Kitchen", "total_revenue": 129.99},
        {"product_category": "Books", "total_revenue": 121.94},
        {"product_category": "Sports", "total_revenue": 67.49},
        {"product_category": "Beauty", "total_revenue": 66.48},
    ]
    insight = (
        "Electronics generated the highest total revenue at $1,132.46, followed by Fashion at $276.95. "
        "Home & Kitchen, Books, Sports, and Beauty generated lower revenues, ranging from $129.99 down to $66.48."
    )
    result = verify_insight(insight, rows)

    assert result["verified"] is True
    assert result["claims_contradictions"] == 0
    assert result["badge"] == "100% Verified Ground Truth"

    # Find the $66.48 claim
    claim_66 = next(c for c in result["claims"] if "$66.48" in c["claimed_value"])
    assert claim_66["status"] == "VERIFIED"
    assert "Beauty" in claim_66["explanation"]
    assert "Sports" not in claim_66["explanation"]
    assert "exactly" in claim_66["explanation"]


def test_flags_invented_numbers():
    rows = [
        {"category": "Electronics", "revenue": 145200.0},
        {"category": "Fashion", "revenue": 98700.0},
    ]
    # $850,000 for Electronics is a contradiction (real revenue is 145,200)
    insight1 = "Electronics produced $850,000 in total sales."
    result1 = verify_insight(insight1, rows)
    assert result1["verified"] is False
    contradictions = [c for c in result1["claims"] if c["status"] == "CONTRADICTION"]
    assert len(contradictions) >= 1

    # 750,000 has no entity or column association anywhere -> unverified
    insight2 = "Overall industry had 750,000 total transactions."
    result2 = verify_insight(insight2, rows)
    assert result2["verified"] is False
    unverified = [c for c in result2["claims"] if c["status"] == "UNVERIFIED"]
    assert len(unverified) >= 1


def test_deliberate_false_entity_number_contradiction():
    """Validates that a deliberately falsified number for an entity is flagged as CONTRADICTION."""
    rows = [
        {"product_category": "Electronics", "total_revenue": 1132.46},
        {"product_category": "Beauty", "total_revenue": 66.48},
    ]
    insight = "Beauty generated $500.00 in total revenue."
    result = verify_insight(insight, rows)

    assert result["verified"] is False
    assert result["claims_contradictions"] >= 1
    assert "Contradiction Detected" in result["badge"]
    claim = result["claims"][0]
    assert claim["status"] == "CONTRADICTION"
    assert "66.48" in claim["explanation"]
    assert "$500.00" in claim["explanation"]


def test_handles_empty_result_set():
    result = verify_insight("No records found for this period.", [])
    assert result["verified"] is True
    assert "Empty" in result["badge"]


def test_detects_superlative_entity_contradiction():
    # Audit Case: Category B is claimed highest with $100, but B is 50 and A is 100
    rows = [
        {"category": "Category A", "revenue": 100.0},
        {"category": "Category B", "revenue": 50.0},
    ]
    insight = "Category B has the highest revenue at $100."
    result = verify_insight(insight, rows)

    assert result["verified"] is False
    assert result["claims_contradictions"] >= 1
    contradictions = [c for c in result["claims"] if c["status"] == "CONTRADICTION"]
    assert len(contradictions) >= 1
    assert "Category B" in contradictions[0]["explanation"]
    assert "Category A" in contradictions[0]["explanation"]
