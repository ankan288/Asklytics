"""Ambiguity Detection & Disambiguation Service (AmbiSQL & Sphinteract).
Detects underspecified, polysemic business phrasing (e.g., 'best category', 'top region', 'sales performance')
and generates multi-choice clarification chips before executing unintended SQL."""

import re
from typing import Dict, List, Optional, Any


# Rules for detecting underspecified or polysemic terminology
AMBIGUITY_PATTERNS = [
    {
        "pattern": re.compile(r"\b(best|top|greatest|leading)\s+(product|category|category|item)\b", re.IGNORECASE),
        "excluded": re.compile(r"\b(by|based on|in terms of|revenue|rating|sales|units|quantity)\b", re.IGNORECASE),
        "question": "How would you like to evaluate the 'best' category?",
        "options": [
            {
                "label": "Total Revenue",
                "subtext": "Ranked by SUM(total_revenue)",
                "refined_prompt": "What is the best product category by total revenue?",
            },
            {
                "label": "Units Sold",
                "subtext": "Ranked by SUM(quantity_sold)",
                "refined_prompt": "What is the best product category by total units sold?",
            },
            {
                "label": "Customer Rating",
                "subtext": "Ranked by AVG(rating)",
                "refined_prompt": "What is the best product category by average customer rating?",
            },
        ],
    },
    {
        "pattern": re.compile(r"\b(top|best|leading)\s+(region|market|location)\b", re.IGNORECASE),
        "excluded": re.compile(r"\b(by|revenue|sales|volume|orders|customers)\b", re.IGNORECASE),
        "question": "How would you like to measure top region?",
        "options": [
            {
                "label": "Highest Total Revenue",
                "subtext": "Ranked by total revenue",
                "refined_prompt": "Which region has the highest total revenue?",
            },
            {
                "label": "Most Orders Sold",
                "subtext": "Ranked by total units sold",
                "refined_prompt": "Which region has the highest number of units sold?",
            },
            {
                "label": "Highest Average Rating",
                "subtext": "Ranked by customer satisfaction",
                "refined_prompt": "Which region has the highest average customer rating?",
            },
        ],
    },
    {
        "pattern": re.compile(r"\b(recent|latest)\s+(sales|transactions|orders|performance)\b", re.IGNORECASE),
        "excluded": re.compile(r"\b(2022|2023|month|last\s+\d+|from|since)\b", re.IGNORECASE),
        "question": "Which timeframe do you mean by 'recent'?",
        "options": [
            {
                "label": "Year 2023",
                "subtext": "Filter to order_date >= '2023-01-01'",
                "refined_prompt": "Show sales trend for 2023.",
            },
            {
                "label": "Last 90 Days",
                "subtext": "Filter to most recent 3 months",
                "refined_prompt": "Show sales for the last 90 days of records.",
            },
            {
                "label": "Entire Historical Dataset",
                "subtext": "Include all 2022-2023 records",
                "refined_prompt": "Show sales across the full dataset.",
            },
        ],
    },
    {
        "pattern": re.compile(r"\b(payment\s+method\s+performance|performance\s+by\s+payment)\b", re.IGNORECASE),
        "excluded": re.compile(r"\b(revenue|rating|volume|count)\b", re.IGNORECASE),
        "question": "What metric defines 'performance' for payment methods?",
        "options": [
            {
                "label": "Revenue Generated",
                "subtext": "SUM(total_revenue)",
                "refined_prompt": "Compare total revenue by payment method.",
            },
            {
                "label": "Transaction Volume",
                "subtext": "COUNT(order_id)",
                "refined_prompt": "Compare number of orders by payment method.",
            },
            {
                "label": "Customer Satisfaction",
                "subtext": "AVG(rating)",
                "refined_prompt": "Compare average customer rating by payment method.",
            },
        ],
    },
]


def check_ambiguity(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Evaluates whether a natural-language query contains ambiguous phrasing.
    Returns:
        None if unambiguous, or Dict with question and clarification options.
    """
    clean = prompt.strip()
    for rule in AMBIGUITY_PATTERNS:
        match = rule["pattern"].search(clean)
        if match:
            # Check if user already provided qualifying criteria
            if not rule["excluded"].search(clean):
                return {
                    "is_ambiguous": True,
                    "matched_term": match.group(0),
                    "question": rule["question"],
                    "options": rule["options"],
                }
    return None
