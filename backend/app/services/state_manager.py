"""Structured Conversation State Manager (Upgrade #5).
Maintains active analytical context across multi-turn sessions:
- Active metric (e.g., total_revenue, units_sold, average_rating)
- Active dimensions (e.g., category, region, payment_method)
- Active filters (e.g., year=2023, category='Electronics')
Injects explicit context into downstream LLM planning prompts to prevent drift."""

import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class ConversationState(BaseModel):
    session_id: str
    active_metric: Optional[str] = None
    active_dimensions: List[str] = []
    active_filters: Dict[str, str] = {}
    last_sql: Optional[str] = None
    turn_count: int = 0


_SESSION_STATES: Dict[str, ConversationState] = {}


def get_conversation_state(session_id: str) -> ConversationState:
    """Retrieves or initializes structured analytical state for a session."""
    if session_id not in _SESSION_STATES:
        _SESSION_STATES[session_id] = ConversationState(session_id=session_id)
    return _SESSION_STATES[session_id]


def update_state_from_turn(
    session_id: str,
    prompt: str,
    sql: str,
    columns: Optional[List[str]] = None,
) -> ConversationState:
    """
    Introspects executed SQL and user prompt to update persistent analytical state.
    """
    state = get_conversation_state(session_id)
    state.turn_count += 1
    state.last_sql = sql

    sql_upper = sql.upper()

    # 1. Infer active metric
    metric_candidates = [
        ("TOTAL_REVENUE", "total_revenue"),
        ("REVENUE", "total_revenue"),
        ("QUANTITY_SOLD", "quantity_sold"),
        ("QUANTITY", "quantity_sold"),
        ("RATING", "rating"),
        ("PRICE", "unit_price"),
    ]
    for pattern, metric in metric_candidates:
        if pattern in sql_upper:
            state.active_metric = metric
            break

    # 2. Infer active dimensions from GROUP BY or prompt
    dim_candidates = ["category", "region", "payment_method", "order_date"]
    new_dims = []
    if "GROUP BY" in sql_upper:
        group_part = sql_upper.split("GROUP BY")[1].split("ORDER BY")[0].split("LIMIT")[0]
        for dim in dim_candidates:
            if dim.upper() in group_part:
                new_dims.append(dim)
    if new_dims:
        state.active_dimensions = new_dims

    # 3. Infer active filters from WHERE clause
    if "WHERE" in sql_upper:
        where_part = sql_upper.split("WHERE")[1].split("GROUP BY")[0].split("ORDER BY")[0].split("LIMIT")[0]
        # Look for year filter
        year_match = re.search(r"202[2-5]", where_part)
        if year_match:
            state.active_filters["year"] = year_match.group(0)
        # Look for category filter
        for cat in ["Electronics", "Clothing", "Home", "Books"]:
            if cat.upper() in where_part:
                state.active_filters["category"] = cat

    _SESSION_STATES[session_id] = state
    return state


def build_state_prompt_context(session_id: str) -> str:
    """Formats active state for injection into the LLM system prompt."""
    state = get_conversation_state(session_id)
    if state.turn_count == 0:
        return ""

    parts = [
        "\n--- Structured Analytical State (Multi-Turn Context) ---",
        f"Active Metric: {state.active_metric or 'None specified'}",
        f"Active Dimensions: {', '.join(state.active_dimensions) if state.active_dimensions else 'None specified'}",
    ]
    if state.active_filters:
        filters_str = ", ".join(f"{k}={v}" for k, v in state.active_filters.items())
        parts.append(f"Active Filters: {filters_str}")
    if state.last_sql:
        parts.append(f"Previous SQL: {state.last_sql}")
    parts.append("Note: If user asks a follow-up (e.g., 'break that down by region' or 'now filter for 2023'), preserve the active metric/filters.\n")

    return "\n".join(parts)


def reset_conversation_state(session_id: str) -> None:
    """Resets state for a cleared session."""
    if session_id in _SESSION_STATES:
        del _SESSION_STATES[session_id]
