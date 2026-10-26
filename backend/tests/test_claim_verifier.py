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
    assert "Contradiction Detected" in result["badge"]
