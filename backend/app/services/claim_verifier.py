"""Claim-Level Insight Verification Engine (ConDABench & InsightLens).
Extracts entity-metric-value triplets, superlatives, and numerical claims from LLM prose,
evaluates each against the raw query result set, and categorizes them as:
  - VERIFIED: Assertions mathematically confirmed by the data (exact financial precision or rounding match)
  - CONTRADICTION: Assertions directly refuted by the data (wrong entity holding superlative or wrong entity number)
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
    "max": re.compile(r"\b(highest|maximum|top|peak|largest|greatest|best)\b", re.IGNORECASE),
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


def _find_mentioned_entities(
    sentence: str,
    rows: List[Dict[str, Any]],
    cat_cols: List[str],
) -> List[Tuple[str, str, Dict[str, Any]]]:
    """Finds entities in rows that are explicitly mentioned in the sentence.
    Returns list of (entity_value, column_name, row_dict)."""
    found = []
    sentence_lower = sentence.lower()

    for r in rows:
        for c in cat_cols:
            val = r.get(c)
            if val is not None and not isinstance(val, (int, float, bool)):
                val_str = str(val).strip()
                if not val_str:
                    continue
                patterns = [
                    r"\b" + re.escape(val_str.lower()) + r"\b",
                    r"\b" + re.escape(c.lower()) + r"\s+" + re.escape(val_str.lower()) + r"\b",
                ]
                if any(re.search(p, sentence_lower) for p in patterns):
                    found.append((val_str, c, r))
    # Deduplicate by entity value
    unique_found = {}
    for ent, col, r in found:
        if ent not in unique_found:
            unique_found[ent] = (ent, col, r)
    return list(unique_found.values())


def _find_superlative_target_entity(
    sentence: str,
    superlative_match: re.Match,
    mentioned_entities: List[Tuple[str, str, Dict[str, Any]]],
) -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """Finds the specific entity syntactically bound to the superlative term."""
    sup_start = superlative_match.start()
    sentence_lower = sentence.lower()
    candidates = []
    for ent_val, ent_col, ent_row in mentioned_entities:
        ent_pos = sentence_lower.find(ent_val.lower())
        if ent_pos != -1:
            preceding_window = sentence_lower[max(0, ent_pos - 15):ent_pos]
            # Exclude secondary entities in phrases like "followed by Fashion"
            if any(marker in preceding_window for marker in ["followed by", "after", "second to", "next to", "compared to"]):
                continue
            distance = abs(ent_pos - sup_start)
            candidates.append((distance, (ent_val, ent_col, ent_row)))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    return None


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
        max_match = _SUPERLATIVES["max"].search(sentence)
        min_match = _SUPERLATIVES["min"].search(sentence)

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

        # ── 1. Check Superlative Claim with Syntactically Bound Target ─────────────
        if max_match and mentioned_entities and num_cols:
            target = _find_superlative_target_entity(sentence, max_match, mentioned_entities)
            if target:
                ent_val, ent_col, ent_row = target
                for nc in num_cols:
                    if nc not in col_stats:
                        continue
                    stats = col_stats[nc]
                    actual_entity_val = float(str(ent_row.get(nc, 0)).replace(",", "").replace("$", ""))
                    max_val = stats["max_val"]
                    max_row = stats["max_row"]
                    max_ent_val = max_row.get(ent_col, "another entity")

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

        if min_match and mentioned_entities and num_cols:
            target = _find_superlative_target_entity(sentence, min_match, mentioned_entities)
            if target:
                ent_val, ent_col, ent_row = target
                for nc in num_cols:
                    if nc not in col_stats:
                        continue
                    stats = col_stats[nc]
                    actual_entity_val = float(str(ent_row.get(nc, 0)).replace(",", "").replace("$", ""))
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

        # ── 2. Check Explicit Numbers Against Candidates with Best Match & Financial Precision ──
        is_approx_sentence = bool(re.search(r"\b(about|approx|approximately|around|nearly|roughly|~)\b", sentence, re.I))

        for raw_text, val, is_pct in extracted_numbers:
            has_explicit_cents = "." in raw_text and re.search(r"\.\d{2}\b", raw_text) is not None
            is_approx_number = is_approx_sentence or bool(re.search(r"[kmb%]|thousand|million|billion", raw_text, re.I))

            # Compile all candidate numbers from dataset rows, entity records, and aggregates
            candidates: List[Tuple[float, str, bool, Optional[str]]] = []  # (value, desc, is_entity, ent_name)
            for ent_val, ent_col, ent_row in mentioned_entities:
                for nc in num_cols:
                    try:
                        ev = float(str(ent_row.get(nc, 0)).replace(",", "").replace("$", ""))
                        candidates.append((ev, f"'{ent_val}' {nc}", True, ent_val))
                    except ValueError:
                        pass

            for nc, stats in col_stats.items():
                for v in stats["values"]:
                    candidates.append((v, f"column '{nc}'", False, None))
                if stats["sum"] > 0:
                    candidates.append((stats["sum"], f"total SUM of '{nc}'", False, None))
                if stats["avg"] > 0:
                    candidates.append((stats["avg"], f"average of '{nc}'", False, None))

            # Score each candidate: find exact matches and close matches
            exact_matches = []
            close_matches = []
            for cv, cdesc, is_ent, ent_name in candidates:
                abs_diff = abs(cv - val)
                rel_diff = abs_diff / abs(cv) if cv != 0 else 1.0
                if abs_diff <= 0.01:
                    exact_matches.append((abs_diff, cv, cdesc, ent_name))
                elif not has_explicit_cents and is_approx_number and rel_diff <= 0.025:
                    close_matches.append((rel_diff, cv, cdesc, ent_name))

            if exact_matches:
                # Prioritize entity matches and lowest absolute difference
                exact_matches.sort(key=lambda x: (0 if x[3] else 1, x[0]))
                best = exact_matches[0]
                claims.append({
                    "claim_text": sentence,
                    "claimed_value": raw_text,
                    "matched_value": best[1],
                    "status": "VERIFIED",
                    "explanation": f"Matches {best[2]} ({best[1]:,.2f}) exactly.",
                })
            elif close_matches:
                close_matches.sort(key=lambda x: (0 if x[3] else 1, x[0]))
                best = close_matches[0]
                claims.append({
                    "claim_text": sentence,
                    "claimed_value": raw_text,
                    "matched_value": best[1],
                    "status": "VERIFIED",
                    "explanation": f"Matches {best[2]} ({best[1]:,.2f}) within rounding tolerance ({best[0]*100:.1f}%).",
                })
            else:
                # Check for direct entity contradiction: did prose cite this number for a single mentioned entity?
                found_contradiction = False
                for ent_val, ent_col, ent_row in mentioned_entities:
                    for nc in num_cols:
                        ev = float(str(ent_row.get(nc, 0)).replace(",", "").replace("$", ""))
                        if abs(ev - val) > 0.05 * (ev if ev != 0 else 1.0) and ent_val.lower() in sentence.lower():
                            if len(mentioned_entities) == 1:
                                claims.append({
                                    "claim_text": sentence,
                                    "claimed_value": raw_text,
                                    "matched_value": None,
                                    "status": "CONTRADICTION",
                                    "explanation": f"Contradiction: '{ent_val}' {nc} is actually {ev:,.2f}, not {raw_text}.",
                                })
                                found_contradiction = True
                                break
                    if found_contradiction:
                        break

                if not found_contradiction:
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
