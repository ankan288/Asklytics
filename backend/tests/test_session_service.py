"""Production test suite for Session Management Service (TTL, history ring-buffer, multi-turn tracking)."""

import time
import pytest
from app.services import session_service


def test_create_session():
    sid = session_service.create_session("default")
    assert sid is not None
    assert len(sid) == 36  # Standard UUID length
    session = session_service.get_session(sid)
    assert session is not None
    assert session["datasource_id"] == "default"
    assert session["history"] == []


def test_append_and_retrieve_history():
    sid = session_service.create_session("default")
    session_service.append_history(sid, "Prompt 1", "SELECT 1", ["Chart 1"])
    session_service.append_history(sid, "Prompt 2", "SELECT 2", ["Chart 2"])

    history = session_service.get_history(sid)
    assert len(history) == 2
    assert history[0]["user_prompt"] == "Prompt 1"
    assert history[1]["user_prompt"] == "Prompt 2"


def test_max_history_ring_buffer():
    sid = session_service.create_session("default")
    # Append 15 turns
    for i in range(15):
        session_service.append_history(sid, f"Prompt {i}", f"SELECT {i}", [f"Chart {i}"])

    history = session_service.get_history(sid)
    # Must be capped at MAX_HISTORY (10)
    assert len(history) == 10
    # Last turn should be Prompt 14
    assert history[-1]["user_prompt"] == "Prompt 14"
    # First turn in ring buffer should be Prompt 5
    assert history[0]["user_prompt"] == "Prompt 5"


def test_delete_session():
    sid = session_service.create_session("default")
    assert session_service.get_session(sid) is not None
    deleted = session_service.delete_session(sid)
    assert deleted is True
    assert session_service.get_session(sid) is None


def test_expired_session_cleanup():
    sid = session_service.create_session("default")
    session = session_service.get_session(sid)
    # Artificially age the session beyond TTL (3600 seconds)
    session["last_used"] = time.time() - 3700

    session_service._cleanup_expired()
    # Now it should be garbage-collected
    assert session_service.get_session(sid) is None
