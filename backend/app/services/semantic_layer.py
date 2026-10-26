"""Semantic Layer & Metric Store (Upgrade #8).
Defines standard business metrics, calculated formulas, dimensions, and synonym mappings.
Prevents semantic misalignment by providing verified SQL expressions to LLM planners."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class MetricDefinition(BaseModel):
    name: str
    label: str
    sql_formula: str
    description: str
    synonyms: List[str] = []


class DimensionDefinition(BaseModel):
    name: str
    label: str
    sql_column: str
    description: str
    synonyms: List[str] = []


CANONICAL_METRICS: Dict[str, MetricDefinition] = {
    "revenue": MetricDefinition(
        name="revenue",
        label="Total Revenue ($)",
        sql_formula="SUM(total_revenue)",
        description="Gross revenue computed as SUM(total_revenue)",
        synonyms=["sales", "turnover", "gross revenue", "total sales", "income"],
    ),
    "units_sold": MetricDefinition(
        name="units_sold",
        label="Units Sold (Qty)",
        sql_formula="SUM(quantity_sold)",
        description="Total quantity of products sold",
        synonyms=["units", "quantity", "volume", "items sold", "products sold"],
    ),
    "average_rating": MetricDefinition(
        name="average_rating",
        label="Average Customer Rating",
        sql_formula="ROUND(AVG(rating), 2)",
        description="Mean customer star rating on a 1-5 scale",
        synonyms=["rating", "satisfaction", "csat", "customer rating", "review score"],
    ),
    "order_count": MetricDefinition(
        name="order_count",
        label="Order Count",
        sql_formula="COUNT(order_id)",
        description="Total count of recorded transactions/orders",
        synonyms=["orders", "transactions", "number of sales", "total orders"],
    ),
}

CANONICAL_DIMENSIONS: Dict[str, DimensionDefinition] = {
    "category": DimensionDefinition(
        name="category",
        label="Product Category",
        sql_column="product_category",
        description="Merchandise category (e.g., Electronics, Clothing, Home)",
        synonyms=["product category", "department", "genre", "product type"],
    ),
    "region": DimensionDefinition(
        name="region",
        label="Geographic Region",
        sql_column="customer_region",
        description="Sales territory (e.g., North America, Europe, Asia)",
        synonyms=["customer region", "territory", "location", "market", "zone"],
    ),
    "payment_method": DimensionDefinition(
        name="payment_method",
        label="Payment Method",
        sql_column="payment_method",
        description="Checkout instrument (e.g., Credit Card, UPI, Debit Card, Net Banking)",
        synonyms=["payment", "payment type", "tender", "checkout method"],
    ),
    "order_date": DimensionDefinition(
        name="order_date",
        label="Order Date",
        sql_column="order_date",
        description="Transaction timestamp in YYYY-MM-DD format",
        synonyms=["date", "time", "day", "month", "year"],
    ),
}


def get_semantic_manifest() -> Dict[str, Any]:
    """Returns serialized semantic catalog for UI and API inspection."""
    return {
        "metrics": [m.model_dump() for m in CANONICAL_METRICS.values()],
        "dimensions": [d.model_dump() for d in CANONICAL_DIMENSIONS.values()],
    }


def format_semantic_prompt_context() -> str:
    """Produces standardized semantic constraints to embed in the LLM planning prompt."""
    lines = ["\n--- Semantic Layer Standards ---"]
    lines.append("Use these canonical metric definitions when generating SQL:")
    for m in CANONICAL_METRICS.values():
        lines.append(f"- {m.label} -> {m.sql_formula} (Synonyms: {', '.join(m.synonyms)})")
    lines.append("Use these canonical dimensions for grouping/filtering:")
    for d in CANONICAL_DIMENSIONS.values():
        lines.append(f"- {d.label} -> column '{d.sql_column}' (Synonyms: {', '.join(d.synonyms)})")
    lines.append("---------------------------------\n")
    return "\n".join(lines)


def resolve_metric(query_phrase: str) -> Optional[MetricDefinition]:
    """Resolves arbitrary user terminology to canonical metric."""
    q = query_phrase.lower()
    for metric in CANONICAL_METRICS.values():
        if metric.name in q:
            return metric
        for syn in metric.synonyms:
            if syn in q:
                return metric
    return None
