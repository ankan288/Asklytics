import pytest
from app.services.state_manager import (
    get_conversation_state,
    update_state_from_turn,
    build_state_prompt_context,
    reset_conversation_state,
)


def test_state_tracking_and_metric_inference():
    sid = "test-session-state-1"
    reset_conversation_state(sid)

    state = update_state_from_turn(
        sid,
        "What is total revenue by category?",
        "SELECT category, SUM(total_revenue) AS total_revenue FROM amazon_sales GROUP BY category;",
    )
    assert state.turn_count == 1
    assert state.active_metric == "total_revenue"
    assert "category" in state.active_dimensions

    context = build_state_prompt_context(sid)
    assert "Active Metric: total_revenue" in context
    assert "category" in context


def test_state_filter_inference():
    sid = "test-session-state-2"
    reset_conversation_state(sid)

    state = update_state_from_turn(
        sid,
        "Filter for Electronics in 2023",
        "SELECT * FROM amazon_sales WHERE category = 'Electronics' AND order_date >= '2023-01-01';",
    )
    assert state.active_filters.get("year") == "2023"
    assert state.active_filters.get("category") == "Electronics"
