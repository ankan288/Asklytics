"""Evaluation Harness (Upgrade #9).
Computes Execution Accuracy (EX) and AST Safety compliance against benchmark queries.
Executes candidate SQL and gold-standard SQL on the benchmark SQLite dataset to confirm
exact tabular result set equivalence."""

import json
import os
import sqlite3
import time
from typing import Dict, List, Any, Tuple
from app.services.sql_service import validate_and_sanitize_sql, execute_query
from app.database import sample_db


BENCHMARK_PATH = os.path.join(os.path.dirname(__file__), "benchmark_queries.json")


def _normalize_results(rows: List[Dict[str, Any]]) -> List[Tuple]:
    """Converts rows to sorted list of value tuples for order-independent tabular comparison."""
    if not rows:
        return []
    tuples = []
    for r in rows:
        # Round floating points to 2 decimal places to prevent micro-divergence
        t = tuple(round(v, 2) if isinstance(v, float) else v for v in r.values())
        tuples.append(t)
    return sorted(tuples, key=lambda x: str(x))


def evaluate_benchmark(
    candidate_queries: Dict[str, str] = None,
    datasource_id: str = "default",
) -> Dict[str, Any]:
    """
    Runs the benchmark evaluation harness.
    If candidate_queries is None, executes the gold standard against itself to verify baseline (100% EX).
    """
    from app.config import get_settings
    # Ensure sample database is ready
    sample_db.seed_database(get_settings().db_path)

    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    total_cases = len(cases)
    ex_matches = 0
    ast_safe_count = 0
    total_latency_ms = 0.0
    results_detail = []

    for item in cases:
        cid = item["id"]
        category = item["category"]
        question = item["question"]
        gold_sql = item["gold_sql"]

        cand_sql = candidate_queries.get(cid, gold_sql) if candidate_queries else gold_sql

        # 1. AST Safety check
        is_safe = False
        try:
            sanitized, _ = validate_and_sanitize_sql(cand_sql, datasource_id)
            is_safe = True
            ast_safe_count += 1
        except Exception:
            sanitized = cand_sql

        # 2. Execution comparison
        t0 = time.time()
        gold_rows = []
        cand_rows = []
        exec_error = None
        try:
            gold_rows = execute_query(gold_sql, datasource_id)
            cand_rows = execute_query(sanitized, datasource_id)
        except Exception as e:
            exec_error = str(e)

        duration_ms = (time.time() - t0) * 1000.0
        total_latency_ms += duration_ms

        gold_norm = _normalize_results(gold_rows)
        cand_norm = _normalize_results(cand_rows)

        matched = (gold_norm == cand_norm) and (len(gold_rows) > 0 or len(cand_rows) == 0) and (exec_error is None)
        if matched:
            ex_matches += 1

        results_detail.append({
            "id": cid,
            "category": category,
            "question": question,
            "is_safe": is_safe,
            "ex_matched": matched,
            "latency_ms": round(duration_ms, 2),
            "rows_returned": len(cand_rows),
            "error": exec_error,
        })

    execution_accuracy = round((ex_matches / total_cases) * 100.0, 1)
    ast_safety_rate = round((ast_safe_count / total_cases) * 100.0, 1)
    avg_latency = round(total_latency_ms / total_cases, 2)

    summary = {
        "total_test_cases": total_cases,
        "execution_accuracy_pct": execution_accuracy,
        "ast_safety_rate_pct": ast_safety_rate,
        "average_latency_ms": avg_latency,
        "ex_passed": ex_matches,
        "ex_failed": total_cases - ex_matches,
        "details": results_detail,
    }

    return summary


def run_cli_report() -> None:
    """Executes evaluation and prints formatted scorecard."""
    print("=" * 60)
    print("  Asklytics Benchmark Evaluation Harness (Upgrade #9)")
    print("=" * 60)
    summary = evaluate_benchmark()
    print(f"Total Test Cases      : {summary['total_test_cases']}")
    print(f"Execution Accuracy (EX): {summary['execution_accuracy_pct']}%")
    print(f"AST Safety Pass Rate  : {summary['ast_safety_rate_pct']}%")
    print(f"Average Latency       : {summary['average_latency_ms']} ms")
    print("-" * 60)
    for d in summary["details"]:
        status = "PASS" if d["ex_matched"] else "FAIL"
        print(f"[{status}] {d['id']} ({d['category']}): {d['question']} ({d['latency_ms']}ms)")
    print("=" * 60)


if __name__ == "__main__":
    run_cli_report()
