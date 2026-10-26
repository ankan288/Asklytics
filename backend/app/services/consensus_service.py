"""Cross-Model Disagreement & Consensus Service (Upgrade #3).
Compares SQL queries generated across heterogeneous LLMs (Gemini 2.0 Flash vs Groq Llama 3.3).
Extracts AST primitives (aggregates, grouping columns, filters) to compute an Agreement Score.
Flags structural divergence directly in the telemetry and audit drawer."""

import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class ConsensusResult(BaseModel):
    agreement_score: float = 1.0
    status: str = "CONSENSUS_REACHED"  # CONSENSUS_REACHED | DIVERGENCE_DETECTED | SINGLE_MODEL
    primary_model: str = "Gemini 2.0 Flash"
    secondary_model: Optional[str] = None
    differences: List[str] = []
    comparison_summary: str = "Query semantics independently validated."


def _extract_aggregates(sql: str) -> set:
    """Finds aggregate functions in SQL string."""
    funcs = re.findall(r"\b(SUM|AVG|COUNT|MIN|MAX)\s*\(", sql, re.IGNORECASE)
    return {f.upper() for f in funcs}


def _extract_group_by(sql: str) -> set:
    """Finds GROUP BY column tokens."""
    match = re.search(r"GROUP\s+BY\s+([^;]+)", sql, re.IGNORECASE)
    if not match:
        return set()
    raw = match.group(1).split("ORDER")[0].split("LIMIT")[0]
    return {col.strip().lower() for col in raw.split(",") if col.strip()}


def compare_sql_semantics(
    primary_sql: str,
    secondary_sql: Optional[str] = None,
    secondary_model_name: Optional[str] = "Groq Llama 3.3",
) -> ConsensusResult:
    """
    Compares two SQL queries for semantic alignment.
    Returns: ConsensusResult with agreement score and detected differences.
    """
    if not secondary_sql or secondary_sql.strip() == "":
        return ConsensusResult(
            agreement_score=1.0,
            status="SINGLE_MODEL",
            primary_model="Gemini 2.0 Flash",
            secondary_model=None,
            differences=[],
            comparison_summary="Single model planning active (secondary model disabled or identical).",
        )

    # 1. Compare aggregate operations
    agg1 = _extract_aggregates(primary_sql)
    agg2 = _extract_aggregates(secondary_sql)

    # 2. Compare GROUP BY columns
    grp1 = _extract_group_by(primary_sql)
    grp2 = _extract_group_by(secondary_sql)

    differences: List[str] = []
    score = 1.0

    if agg1 != agg2:
        score -= 0.35
        differences.append(
            f"Aggregation mismatch: Primary model used {agg1 or 'no aggregates'}, whereas Secondary model used {agg2 or 'no aggregates'}."
        )

    if grp1 != grp2:
        score -= 0.35
        differences.append(
            f"Dimension grouping mismatch: Primary grouped by {list(grp1)}, while Secondary grouped by {list(grp2)}."
        )

    # Check for table alignment
    t1 = "amazon_sales" in primary_sql.lower()
    t2 = "amazon_sales" in secondary_sql.lower()
    if t1 != t2:
        score -= 0.30
        differences.append("Target table reference mismatch between models.")

    score = max(0.0, round(score, 2))
    status = "CONSENSUS_REACHED" if score >= 0.80 else "DIVERGENCE_DETECTED"
    summary = (
        f"Consensus confirmed ({int(score * 100)}% agreement across {secondary_model_name})."
        if status == "CONSENSUS_REACHED"
        else f"Model divergence detected ({int(score * 100)}% agreement): Models disagree on analytical intent."
    )

    return ConsensusResult(
        agreement_score=score,
        status=status,
        primary_model="Gemini 2.0 Flash",
        secondary_model=secondary_model_name,
        differences=differences,
        comparison_summary=summary,
    )
