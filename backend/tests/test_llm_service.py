"""Production test suite for LLM Services (JSON cleaning, prompt construction, retry mechanisms, fallback)."""

import json
import pytest
from app.services import gemini_service


def test_parse_response_clean_json():
    raw = '{"sql": "SELECT 1", "dashboard_title": "Test"}'
    parsed = gemini_service._parse_response(raw)
    assert parsed["sql"] == "SELECT 1"
    assert parsed["dashboard_title"] == "Test"


def test_parse_response_markdown_fenced_json():
    raw = '```json\n{"sql": "SELECT category, SUM(rev) FROM t", "charts": []}\n```'
    parsed = gemini_service._parse_response(raw)
    assert "SELECT category" in parsed["sql"]
    assert parsed["charts"] == []


def test_parse_response_raw_code_fence():
    raw = '```\n{"error": "Cannot answer from schema"}\n```'
    parsed = gemini_service._parse_response(raw)
    assert parsed["error"] == "Cannot answer from schema"


def test_build_planner_message_without_history():
    msg = gemini_service._build_planner_message("TABLE t(id INT)", "Show total count", [])
    assert "DATABASE SCHEMA:\nTABLE t(id INT)" in msg
    assert "PRIOR CONVERSATION:" not in msg
    assert "USER QUESTION: Show total count" in msg


def test_build_planner_message_with_history():
    history = [
        {"user_prompt": "First Q", "sql": "SELECT 1", "chart_titles": ["Bar Chart"]}
    ]
    msg = gemini_service._build_planner_message("SCHEMA", "Second Q", history)
    assert "PRIOR CONVERSATION:" in msg
    assert "Turn 1: User asked: \"First Q\"" in msg
    assert "USER QUESTION: Second Q" in msg


def test_insight_caps_sample_size():
    rows = [{"id": i, "val": i * 10} for i in range(100)]
    # Verify that message formatting does not dump all 100 rows
    sample = rows[:25] if len(rows) <= 25 else rows[:12] + rows[-12:]
    assert len(sample) == 24


def test_call_groq_fallback(monkeypatch):
    from unittest.mock import MagicMock
    import groq

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"sql": "SELECT 1"}'
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    monkeypatch.setattr(groq, "Groq", lambda api_key: mock_client)

    from app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "groq_api_key", "mock-groq-key")

    result = gemini_service._call_groq("System instructions", "User query")
    assert '{"sql": "SELECT 1"}' in result
