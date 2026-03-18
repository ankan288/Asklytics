"""LLM API integration — Stage 1: query planning, Stage 2: grounded insight.
   Supports Gemini (primary) with Grok fallback on failure."""
import json, logging, re
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Stage 1: SQL + chart spec generation ──────────────────────────────────────
# insight_summary deliberately excluded — it's generated in Stage 2 once we
# have the actual query results, so insights are always grounded in real data.

PLANNER_PROMPT = """You are a senior data analyst assistant embedded in a business intelligence dashboard.

You will receive:
1. A compact database schema with column names, data types, value ranges, and 2 sample rows
2. A user's natural-language business question
3. (Optional) Prior conversation turns for follow-up context

Your job is to respond ONLY with a single valid JSON object — no markdown, no explanation text.

The JSON must match this exact structure:
{
  "dashboard_title": "Short descriptive title for the whole dashboard",
  "sql": "A single read-only SELECT statement. Use only columns that exist in the schema.",
  "charts": [
    {
      "id": "chart-1",
      "type": "line | bar | pie | area | kpi",
      "title": "Chart title",
      "x_key": "column name for x-axis or label",
      "y_keys": ["one or more column names for values"],
      "color_palette": ["#hex1", "#hex2"]
    }
  ],
  "follow_up_suggestions": ["A natural follow-up question", "Another angle to explore", "A drill-down suggestion"]
}

Chart type selection rules:
- "line"  → time-series data, trends over time
- "area"  → same as line but emphasise volume/cumulative totals
- "bar"   → comparing values across categories
- "pie"   → parts of a whole (use only if <= 7 categories)
- "kpi"   → a single aggregated scalar number (no axis needed)

You may return multiple chart objects if the question has multiple angles.

If the question CANNOT be answered from the available schema, return ONLY:
{ "error": "Clear explanation of why the question cannot be answered from this data." }

RULES:
- NEVER fabricate data or column names that do not exist in the schema.
- NEVER return INSERT, UPDATE, DELETE, DROP, or any non-SELECT SQL.
- ALWAYS use column names from the provided schema exactly as listed.
- Use the COLUMN STATS section to understand valid value ranges — do not use values outside those ranges.
- Keep SQL compatible with SQLite syntax.
- For time-series, use strftime('%Y-%m', order_date) to group by month."""


# ── Stage 2: Grounded insight from actual query results ────────────────────────
# This runs AFTER SQL execution, so insights reference real numbers from the DB.

INSIGHT_PROMPT = """You are a senior data analyst. You will receive a business question, the SQL used, and the ACTUAL rows returned by the database query.

Respond ONLY with a valid JSON object — no markdown, no explanation text:
{
  "insight_summary": "1-2 sentence plain-English insight. Reference specific numbers from the actual data.",
  "data_limitations": "One sentence describing what this dataset CANNOT answer for this question, or null if fully answered."
}

RULES:
- Base insight_summary ONLY on the provided data rows. Never invent numbers.
- If the result set is empty, state that no records matched the criteria.
- If only some aspects of the question are covered by the data, set data_limitations to explain what's missing.
- Keep insight_summary under 60 words.
- data_limitations must be null (JSON null) if the data fully answers the question."""


def _build_planner_message(schema: str, prompt: str, history: list[dict]) -> str:
    parts = [f"DATABASE SCHEMA:\n{schema}\n"]
    if history:
        parts.append("PRIOR CONVERSATION:")
        for i, turn in enumerate(history, 1):
            parts.append(
                f"  Turn {i}: User asked: \"{turn['user_prompt']}\"\n"
                f"  SQL used: {turn['sql']}\n"
                f"  Charts: {turn['chart_titles']}"
            )
        parts.append("")
    parts.append(f"USER QUESTION: {prompt}")
    return "\n".join(parts)


def _parse_response(text: str) -> dict:
    """Extract JSON from Gemini's response, stripping any markdown fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _call_groq(system: str, message: str) -> str:
    """Free fallback: Call Groq API (OpenAI-compatible, completely free)."""
    from openai import OpenAI
    settings = get_settings()
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in .env")

    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content


def _call_llm(system: str, message: str) -> str:
    """Call LLM with automatic fallback: Gemini -> Groq."""
    settings = get_settings()

    # Try Gemini first
    if settings.gemini_api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=settings.gemini_api_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0.1,
                ),
            )
            return response.text
        except Exception as e:
            logger.warning(f"Gemini failed, switching to Groq fallback: {e}")

    # Fallback to Groq (free)
    if settings.groq_api_key:
        try:
            return _call_groq(system, message)
        except Exception as e:
            logger.error(f"All LLM providers failed. Groq error: {e}")
            raise

    raise ValueError("No LLM API keys configured (GEMINI_API_KEY or GROQ_API_KEY)")


def _call_gemini(system: str, message: str) -> str:
    """Wrapper for backward compatibility - uses _call_llm with fallback."""
    return _call_llm(system, message)


def generate_dashboard(schema: str, prompt: str, history: list[dict]) -> dict:
    """Stage 1 — Generate SQL + chart specs from schema and user question."""
    message = _build_planner_message(schema, prompt, history)
    raw = _call_gemini(PLANNER_PROMPT, message)
    try:
        return _parse_response(raw)
    except json.JSONDecodeError:
        logger.warning("Stage 1 first parse failed, retrying...")
        retry = message + "\n\nIMPORTANT: Respond with ONLY valid JSON, no other text."
        raw2 = _call_gemini(PLANNER_PROMPT, retry)
        try:
            return _parse_response(raw2)
        except json.JSONDecodeError as e:
            logger.error(f"Stage 1 both parse attempts failed: {e}")
            return {"error": "AI returned an unparseable response. Please rephrase your question."}


def generate_insight(prompt: str, sql: str, rows: list[dict]) -> dict:
    """Stage 2 — Generate insight grounded in actual query results.

    This runs AFTER SQL execution so the summary is always based on real data,
    never on the model's prediction of what the data might contain.
    """
    # Cap rows to avoid token overflow; preserve first and last for range context
    sample = rows[:25] if len(rows) <= 25 else rows[:12] + rows[-12:]
    message = (
        f"BUSINESS QUESTION: {prompt}\n\n"
        f"SQL USED: {sql}\n\n"
        f"ACTUAL DATA ({len(rows)} total rows, showing up to 25):\n"
        f"{json.dumps(sample, default=str, indent=2)}"
    )
    raw = _call_gemini(INSIGHT_PROMPT, message)
    try:
        parsed = _parse_response(raw)
        return {
            "insight_summary": parsed.get("insight_summary", ""),
            "data_limitations": parsed.get("data_limitations") or None,
        }
    except json.JSONDecodeError as e:
        logger.warning(f"Stage 2 insight parse failed: {e}")
        return {"insight_summary": raw[:200], "data_limitations": None}
