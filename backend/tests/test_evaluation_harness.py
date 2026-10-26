import pytest
from app.evaluation.evaluator import evaluate_benchmark


def test_evaluation_benchmark_execution_accuracy_threshold():
    """Validates that the benchmark test suite achieves >= 80% Execution Accuracy (EX)."""
    summary = evaluate_benchmark()
    assert summary["total_test_cases"] >= 15
    assert summary["execution_accuracy_pct"] >= 80.0, f"EX fell below 80%: {summary['execution_accuracy_pct']}%"
    assert summary["ast_safety_rate_pct"] == 100.0, "AST safety validation failed on benchmark queries"
    assert summary["average_latency_ms"] < 500.0, f"Average latency too high: {summary['average_latency_ms']}ms"
