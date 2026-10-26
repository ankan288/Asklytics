import pytest
from app.services.semantic_layer import (
    get_semantic_manifest,
    format_semantic_prompt_context,
    resolve_metric,
)


def test_semantic_manifest_structure():
    manifest = get_semantic_manifest()
    assert "metrics" in manifest
    assert "dimensions" in manifest
    metric_names = [m["name"] for m in manifest["metrics"]]
    assert "revenue" in metric_names
    assert "units_sold" in metric_names
    assert "average_rating" in metric_names


def test_resolve_metric_synonyms():
    # User says "sales" -> resolves to revenue
    m1 = resolve_metric("What are total sales?")
    assert m1 is not None
    assert m1.name == "revenue"

    # User says "satisfaction" -> resolves to average_rating
    m2 = resolve_metric("Show customer satisfaction")
    assert m2 is not None
    assert m2.name == "average_rating"


def test_format_semantic_prompt():
    prompt = format_semantic_prompt_context()
    assert "SUM(total_revenue)" in prompt
    assert "product_category" in prompt
