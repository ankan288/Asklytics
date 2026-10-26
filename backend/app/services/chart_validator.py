"""Chart Validity & Grammar-of-Graphics Heuristic Checker (VisEval).
Deterministically audits and sanitizes chart recommendations:
- Transforms pie charts with >7 categories into horizontal bar charts.
- Converts line charts with non-temporal / discrete categorical x-axes into bar charts.
- Enforces single-scalar values for KPI cards.
- Provides accessible color palettes and clean data bindings."""

import re
from typing import List, Dict, Any, Tuple


# Regex pattern to identify dates, months, timestamps, or years in x-axis values
TEMPORAL_PATTERN = re.compile(
    r"^(\d{4}[-/]\d{1,2}([-/]\d{1,2})?|\d{4}|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|q[1-4]|w\d{1,2})$",
    re.IGNORECASE,
)

DEFAULT_PALETTE = ["#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626", "#0891B2"]


def _is_temporal_sequence(values: List[Any]) -> bool:
    """Heuristic to check if a sequence of values represents a temporal/sequential axis."""
    if not values:
        return False
    sample = [str(v).strip() for v in values[:10] if v is not None]
    if not sample:
        return False
    match_count = sum(1 for v in sample if TEMPORAL_PATTERN.search(v))
    return match_count / len(sample) >= 0.5


def validate_and_sanitize_charts(
    raw_charts: List[Dict[str, Any]],
    rows: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Validates chart specifications against VisEval visual ergonomics rules.
    Returns:
        (sanitized_charts, audit_corrections)
    """
    sanitized: List[Dict[str, Any]] = []
    corrections: List[str] = []

    for i, chart in enumerate(raw_charts):
        c = dict(chart)
        c_type = c.get("type", "bar").lower()
        title = c.get("title", f"Chart {i+1}")
        x_key = c.get("x_key")
        y_keys = c.get("y_keys", [])
        if not c.get("color_palette"):
            c["color_palette"] = DEFAULT_PALETTE

        # Rule 1: Pie chart slice ceiling (Cleveland & McGill visual perception hierarchy)
        # Pie charts with > 7 categories fail perceptual accuracy tests
        if c_type == "pie":
            num_categories = len(rows)
            if num_categories > 7:
                c["type"] = "bar"
                c_type = "bar"
                corrections.append(
                    f"VisEval Rule: Auto-converted pie chart '{title}' with {num_categories} slices to horizontal bar chart (pie slices > 7 degrade visual perception)."
                )

        # Rule 2: Line chart continuity requirement
        # Line charts imply continuous trend; categorical discrete dimensions must use bar charts
        if c_type == "line" and x_key and rows:
            x_values = [r.get(x_key) for r in rows if r.get(x_key) is not None]
            if not _is_temporal_sequence(x_values):
                c["type"] = "bar"
                c_type = "bar"
                corrections.append(
                    f"VisEval Rule: Auto-converted line chart '{title}' to bar chart because '{x_key}' is discrete categorical data rather than a continuous temporal sequence."
                )

        # Rule 3: KPI scalar consistency
        if c_type == "kpi":
            if rows:
                primary_key = y_keys[0] if y_keys and y_keys[0] in rows[0] else None
                if not primary_key:
                    # Pick first numeric key or first key
                    num_keys = [k for k, v in rows[0].items() if isinstance(v, (int, float))]
                    primary_key = num_keys[0] if num_keys else list(rows[0].keys())[0]
                    c["y_keys"] = [primary_key]
                c["data"] = [{"value": rows[0][primary_key]}]
            else:
                c["data"] = [{"value": 0}]
        else:
            c["data"] = rows

        sanitized.append(c)

    return sanitized, corrections
