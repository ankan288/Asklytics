"""Claim-Level Insight Verification Engine (ConDABench & InsightLens).
Extracts entity-metric-value triplets, superlatives, and numerical claims from LLM prose,
evaluates each against the raw query result set, and categorizes them as:
  - VERIFIED: Assertions mathematically confirmed by the data
  - CONTRADICTION: Assertions directly refuted by the data (wrong entity or wrong number)
  - UNVERIFIED: Figures not found in the dataset or column stats
"""

import re
import logging
from typing import Any, Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Pattern for numbers with optional currency prefix and scale/unit suffix
_NUMBER_PATTERN = re.compile(
    r"(?:\$|€|£)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|\.[0-9]+)\s*(k|m|b|thousand|million|billion|%)?",
    re.IGNORECASE,
)

_SUPERLATIVES = {
    "max": re.compile(r"\b(highest|maximum|top|most|peak|largest|greatest|best)\b", re.IGNORECASE),
    "min": re.compile(r"\b(lowest|minimum|bottom|least|smallest|worst)\b", re.IGNORECASE),
}


def _parse_numeric_value(raw_val: str, unit: Optional[str]) -> float:
    """Converts extracted text (e.g. '145.2k' or '$1,200') to float."""
    clean = raw_val.replace(",", "").replace("$", "").replace("€", "").replace("£", "").strip()
    try:
        val = float(clean)
    except ValueError:
        return 0.0

    if unit:
        u = unit.lower()
        if u in ("k", "thousand"):
            val *= 1_000
        elif u in ("m", "million"):
            val *= 1_000_000
        elif u in ("b", "billion"):
            val *= 1_000_000_000
    return val


def _extract_column_types(rows: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """Separates columns into categorical (string/entity) and numerical (metric)."""
    if not rows:
        return [], []

    categorical_cols = []
    numerical_cols = []

    for col in rows[0].keys():
        sample_vals = [r.get(col) for r in rows if r.get(col) is not None]
        if not sample_vals:
            continue
        first_val = sample_vals[0]
        if isinstance(first_val, (int, float)) and not isinstance(first_val, bool):
            numerical_cols.append(col)
        elif isinstance(first_val, str):
            try:
                float(first_val.replace(",", "").replace("$", ""))
                numerical_cols.append(col)
            except ValueError:
                categorical_cols.append(col)
        else:
            categorical_cols.append(col)

    return categorical_cols, numerical_cols


def _find_mentioned_entities(sentence: str, rows: List[Dict[str, Any]], cat_cols: List[str]) -> List[Tuple[str, str, Dict[str, Any]]]:
    """Finds entities in rows that are explicitly mentioned in the sentence.
    Returns list of (entity_value, column_name, row_dict)."""
    found = []
    sentence_lower = sentence.lower()

    for r in rows:
        for c in cat_cols:
            val = r.get(c)
            if val and isinstance(val, str) and len(val.strip()) > 1:
                val_str = val.strip()
                # Check for exact word or phrase match
                pattern = r"\b" + re.escape(val_str.lower()) + r"\b"
                if re.search(pattern, sentence_lower):
                    found.append((val_str, c, r))
    # Deduplicate by entity value
    unique_found = {}
    for ent, col, r in found:
        if ent not in unique_found:
            unique_found[ent] = (ent, col, r)
    return list(unique_found.values())


def verify_insight(
    insight_text: str,
    rows: List[Dict[str, Any]],
    sql: str = "",
) -> Dict[str, Any]:
    """
    Rigorously verifies factual consistency of insight text against returned database rows.
    Identifies:
      - Superlative attribution (does the named entity actually hold the max/min?)
      - Numeric value accuracy (does the entity have the claimed number?)
      - Aggregate consistency (do sums/percentages match?)
    """
    if not insight_text or not insight_text.strip():
        return {
            "verified": True,
            "verification_rate": 1.0,
            "claims_total": 0,
            "claims_verified": 0,
            "claims_contradictions": 0,
            "claims_unverified": 0,
            "claims": [],
            "verified_summary": "",
            "badge": "No Claims to Verify",
        }

    if not rows:
        return {
            "verified": True,
            "verification_rate": 1.0,
            "claims_total": 1,
            "claims_verified": 1,
            "claims_contradictions": 0,
            "claims_unverified": 0,
            "claims": [
                {
                    "claim_text": insight_text,
                    "claimed_value": "0 rows",
                    "matched_value": 0,
                    "status": "VERIFIED",
                    "explanation": "Result set is empty; query returned zero rows.",
                }
            ],
            "verified_summary": insight_text,
            "badge": "Verified (Empty Result Set)",
        }

    cat_cols, num_cols = _extract_column_types(rows)

    # Precompute column min, max, sum, and ranking
    col_stats: Dict[str, Dict[str, Any]] = {}
    for nc in num_cols:
        col_values = []
        row_pairs = []
        for r in rows:
            v = r.get(nc)
            if v is not None:
                try:
                    num_v = float(str(v).replace(",", "").replace("$", ""))
                    col_values.append(num_v)
                    row_pairs.append((num_v, r))
                except ValueError:
                    pass

        if col_values:
            max_pair = max(row_pairs, key=lambda x: x[0])
            min_pair = min(row_pairs, key=lambda x: x[0])
            col_stats[nc] = {
                "values": col_values,
                "max_val": max_pair[0],
                "max_row": max_pair[1],
                "min_val": min_pair[0],
                "min_row": min_pair[1],
                "sum": sum(col_values),
                "avg": sum(col_values) / len(col_values),
            }

    # Split into sentences
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", insight_text) if s.strip()]
    claims: List[Dict[str, Any]] = []

    for sentence in sentences:
        mentioned_entities = _find_mentioned_entities(sentence, rows, cat_cols)
        has_max = bool(_SUPERLATIVES["max"].search(sentence))
        has_min = bool(_SUPERLATIVES["min"].search(sentence))

        # Extract numeric mentions in sentence
        number_matches = list(_NUMBER_PATTERN.finditer(sentence))
        extracted_numbers = []
        for m in number_matches:
            raw_text = m.group(0).strip()
            num_val = _parse_numeric_value(m.group(1), m.group(2))
            is_pct = m.group(2) == "%"
            # Filter trivial 1, 2 unless currency
            if num_val in (1.0, 2.0) and not m.group(2) and "$" not in raw_text:
                continue
            extracted_numbers.append((raw_text, num_val, is_pct))

        # ── 1. Check Superlative Claim with Mentioned Entity ─────────────
        if (has_max or has_min) and mentioned_entities and num_cols:
            for ent_val, ent_col, ent_row in mentioned_entities:
                for nc in num_cols:
                    if nc not in col_stats:
                        continue
                    stats = col_stats[nc]
                    actual_entity_val = float(str(ent_row.get(nc, 0)).replace(",", "").replace("$", ""))

                    if has_max:
                        max_val = stats["max_val"]
                        max_row = stats["max_row"]
                        max_ent_val = max_row.get(ent_col, "another entity")

                        # Does the mentioned entity actually have the maximum?
                        if abs(actual_entity_val - max_val) > 0.01:
                            claims.append({
                                "claim_text": sentence,
                                "claimed_value": f"{ent_val} is highest",
                                "matched_value": actual_entity_val,
                                "status": "CONTRADICTION",
                                "explanation": (
                                    f"Contradiction: '{ent_val}' has {nc} of {actual_entity_val:,.2f}, "
                                    f"but the actual highest is '{max_ent_val}' with {max_val:,.2f}."
                                ),
                            })
                        else:
                            claims.append({
                                "claim_text": sentence,
                                "claimed_value": f"{ent_val} is highest",
                                "matched_value": actual_entity_val,
                                "status": "VERIFIED",
                                "explanation": f"Verified: '{ent_val}' holds the maximum {nc} ({actual_entity_val:,.2f}).",
                            })

                    elif has_min:
                        min_val = stats["min_val"]
                        min_row = stats["min_row"]
                        min_ent_val = min_row.get(ent_col, "another entity")

                        if abs(actual_entity_val - min_val) > 0.01:
                            claims.append({
                                "claim_text": sentence,
                                "claimed_value": f"{ent_val} is lowest",
                                "matched_value": actual_entity_val,
                                "status": "CONTRADICTION",
                                "explanation": (
                                    f"Contradiction: '{ent_val}' has {nc} of {actual_entity_val:,.2f}, "
                                    f"but the actual lowest is '{min_ent_val}' with {min_val:,.2f}."
                                ),
                            })
                        else:
                            claims.append({
                                "claim_text": sentence,
                                "claimed_value": f"{ent_val} is lowest",
                                "matched_value": actual_entity_val,
                                "status": "VERIFIED",
                                "explanation": f"Verified: '{ent_val}' holds the minimum {nc} ({actual_entity_val:,.2f}).",
                            })

        # ── 2. Check Explicit Numbers Against Entities and Data ──────────
        for raw_text, val, is_pct in extracted_numbers:
            matched = False
            is_contradiction = False
            best_match_val = None
            explanation = ""

            # Check if number was cited for a specific mentioned entity
            if mentioned_entities and not is_pct:
                for ent_val, ent_col, ent_row in mentioned_entities:
                    for nc in num_cols:
                        try:
                            actual_v = float(str(ent_row.get(nc, 0)).replace(",", "").replace("$", ""))
                        except ValueError:
                            continue
                        if abs(actual_v - val) / (abs(actual_v) if actual_v != 0 else 1.0) <= 0.03:
                            matched = True
                            best_match_val = actual_v
                            explanation = f"Matches '{ent_val}' {nc} ({actual_v:,.2f}) within 3% tolerance."
                            break
                        elif val > 0 and actual_v > 0 and abs(actual_v - val) > 0.05 * actual_v:
                            # Cited a completely wrong number for this entity
                            is_contradiction = True
                            explanation = f"Contradiction: '{ent_val}' {nc} is actually {actual_v:,.2f}, not {raw_text}."
                    if matched:
                        is_contradiction = False
                        break

            # If not matched to entity, check against all numbers in result set
            if not matched and not is_contradiction:
                for nc, stats in col_stats.items():
                    for v in stats["values"]:
                        if v != 0 and abs(v - val) / abs(v) <= 0.03:
                            matched = True
                            best_match_val = v
                            explanation = f"Matches row data in column '{nc}' ({v:,.2f})."
                            break
                    if matched:
                        break

            # Check against aggregates (SUM, AVG, COUNT)
            if not matched and not is_contradiction:
                for nc, stats in col_stats.items():
                    total = stats["sum"]
                    avg = stats["avg"]
                    if total > 0 and abs(total - val) / total <= 0.03:
                        matched = True
                        best_match_val = total
                        explanation = f"Matches total SUM of '{nc}' ({total:,.2f})."
                        break
                    elif avg > 0 and abs(avg - val) / avg <= 0.03:
                        matched = True
                        best_match_val = avg
                        explanation = f"Matches average of '{nc}' ({avg:,.2f})."
                        break

            # Check percentage assertions
            if not matched and is_pct:
                for nc, stats in col_stats.items():
                    total = stats["sum"]
                    if total > 0:
                        for row_v in stats["values"]:
                            calc_pct = (row_v / total) * 100
                            if abs(calc_pct - val) <= 2.5:
                                matched = True
                                best_match_val = calc_pct
                                explanation = f"Matches percentage of total for '{nc}' ({calc_pct:.1f}%)."
                                break
                    if matched:
                        break

            if matched:
                claims.append({
                    "claim_text": sentence,
                    "claimed_value": raw_text,
                    "matched_value": best_match_val,
                    "status": "VERIFIED",
                    "explanation": explanation,
                })
            elif is_contradiction:
                claims.append({
                    "claim_text": sentence,
                    "claimed_value": raw_text,
                    "matched_value": None,
                    "status": "CONTRADICTION",
                    "explanation": explanation,
                })
            else:
                claims.append({
                    "claim_text": sentence,
                    "claimed_value": raw_text,
                    "matched_value": None,
                    "status": "UNVERIFIED",
                    "explanation": f"Figure '{raw_text}' not found in query results or column statistics.",
                })

    # Summary calculations
    total_claims = len(claims)
    verified_count = sum(1 for c in claims if c["status"] == "VERIFIED")
    contradiction_count = sum(1 for c in claims if c["status"] == "CONTRADICTION")
    unverified_count = sum(1 for c in claims if c["status"] == "UNVERIFIED")

    if total_claims == 0:
        verified_rate = 1.0
        is_verified = True
        badge = "100% Grounded"
    elif contradiction_count > 0:
        verified_rate = round(verified_count / total_claims, 2)
        is_verified = False
        badge = f"Contradiction Detected ({contradiction_count} conflict{'s' if contradiction_count > 1 else ''})"
    elif unverified_count > 0:
        verified_rate = round(verified_count / total_claims, 2)
        is_verified = verified_rate >= 0.70
        badge = f"{int(verified_rate * 100)}% Verified by Data"
    else:
        verified_rate = 1.0
        is_verified = True
        badge = "100% Verified Ground Truth"

    return {
        "verified": is_verified,
        "verification_rate": verified_rate,
        "claims_total": total_claims,
        "claims_verified": verified_count,
        "claims_contradictions": contradiction_count,
        "claims_unverified": unverified_count,
        "claims": claims,
        "verified_summary": insight_text,
        "badge": badge,
    }
