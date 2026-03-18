"""In-memory session store with TTL and conversation history."""
import uuid, time, logging
from typing import Optional

logger = logging.getLogger(__name__)
SESSION_TTL = 3600  # 1 hour
MAX_HISTORY = 10    # keep last 10 turns per session

_sessions: dict[str, dict] = {}


def create_session(datasource_id: str = "default") -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "datasource_id": datasource_id,
        "history": [],
        "created_at": time.time(),
        "last_used": time.time(),
    }
    _cleanup_expired()
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    s = _sessions.get(session_id)
    if s:
        s["last_used"] = time.time()
    return s


def append_history(session_id: str, user_prompt: str, sql: str, chart_titles: list[str]) -> None:
    s = _sessions.get(session_id)
    if not s:
        return
    s["history"].append({
        "user_prompt": user_prompt,
        "sql": sql,
        "chart_titles": chart_titles,
    })
    # Keep only last MAX_HISTORY turns
    s["history"] = s["history"][-MAX_HISTORY:]


def get_history(session_id: str) -> list[dict]:
    s = _sessions.get(session_id)
    return s["history"] if s else []


def delete_session(session_id: str) -> bool:
    return _sessions.pop(session_id, None) is not None


def _cleanup_expired() -> None:
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if now - s["last_used"] > SESSION_TTL]
    for sid in expired:
        del _sessions[sid]
    if expired:
        logger.info(f"Cleaned up {len(expired)} expired sessions.")
