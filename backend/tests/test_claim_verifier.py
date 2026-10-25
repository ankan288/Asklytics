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


def test_flags_invented_numbers_as_unverified():
    rows = [
        {"category": "Electronics", "revenue": 145200.0},
        {"category": "Fashion", "revenue": 98700.0},
    ]
    # $850,000 is completely made up
    insight = "Electronics produced $850,000 in total sales."
    result = verify_insight(insight, rows)

    assert result["verified"] is False
    unverified = [c for c in result["claims"] if c["status"] == "UNVERIFIED"]
    assert len(unverified) >= 1
    assert "850,000" in unverified[0]["claimed_value"]


def test_handles_empty_result_set():
    result = verify_insight("No records found for this period.", [])
    assert result["verified"] is True
    assert "Empty" in result["badge"]
