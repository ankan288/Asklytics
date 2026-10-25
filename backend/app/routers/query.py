import logging
from fastapi import APIRouter, HTTPException
from app.models.request_models import QueryRequest
from app.models.response_models import DashboardResponse, ChartSpec
from app.services import session_service, schema_service, gemini_service, sql_service
from app.services.supabase_service import create_conversation, add_conversation_turn
import asyncio
import time

router = APIRouter(prefix="/query", tags=["query"])
logger = logging.getLogger(__name__)


@router.post("", response_model=DashboardResponse)
def query(body: QueryRequest):
    # 1. Validate session
    session = session_service.get_session(body.session_id)
    if session is None:
        body.session_id = session_service.create_session(body.datasource_id)

    # 2. Get history and schema
    history = session_service.get_history(body.session_id)
    try:
        schema = schema_service.get_compact_schema(body.datasource_id)
    except ValueError as e:
        if body.datasource_id != "default":
            return DashboardResponse(error="This dataset is no longer available in memory (the dev server may have restarted). Please re-upload your CSV file.")
        return DashboardResponse(error=str(e))

    # 3. Stage 1 — generate SQL + chart specs (no insight yet)
    try:
        ai_response = gemini_service.generate_dashboard(schema, body.prompt, history)
    except ValueError as e:
        return DashboardResponse(error=str(e))
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return DashboardResponse(error=f"AI service unavailable. Details: {str(e)}")

    # 4. Handle AI "cannot answer" response
    if "error" in ai_response and len(ai_response) == 1:
        return DashboardResponse(error=ai_response["error"])

    # 5. Execute SQL against the real database with AST safety & telemetry
    sql = ai_response.get("sql", "")
    telemetry = {}
    try:
        rows, telemetry = sql_service.execute_query_with_telemetry(sql, body.datasource_id)
    except (PermissionError, ValueError) as e:
        return DashboardResponse(
            sql=sql,
            dashboard_title=ai_response.get("dashboard_title", ""),
            error=str(e),
        )

    # 6. Stage 2 — generate insight grounded in actual query results
    # This ensures insight_summary references real numbers, never predicted ones.
    insight_summary = ""
    data_limitations = None
    try:
        insight = gemini_service.generate_insight(body.prompt, sql, rows)
        insight_summary = insight.get("insight_summary", "")
        data_limitations = insight.get("data_limitations")
    except Exception as e:
        logger.warning(f"Insight generation failed (non-fatal): {e}")

    # 6b. Verification Engine — evaluate numerical claims against real rows (ConDABench / InsightLens)
    verification_result = None
    try:
        from app.services import claim_verifier
        from app.models.response_models import VerificationResult, AuditMetadata
        raw_verification = claim_verifier.verify_insight(insight_summary, rows, sql)
        verification_result = VerificationResult(**raw_verification)
    except Exception as e:
        logger.warning(f"Claim verification failed (non-fatal): {e}")

    # 7. Build chart specs with actual data
    raw_charts = ai_response.get("charts", [])
    charts = []
    for i, c in enumerate(raw_charts):
        chart_data = rows
        if c.get("type") == "kpi" and rows:
            y_key = c.get("y_keys", [None])[0]
            if y_key and y_key in rows[0]:
                chart_data = [{"value": rows[0][y_key]}]
        charts.append(ChartSpec(
            id=c.get("id", f"chart-{i+1}"),
            type=c.get("type", "bar"),
            title=c.get("title", ""),
            data=chart_data,
            x_key=c.get("x_key"),
            y_keys=c.get("y_keys", []),
            z_key=c.get("z_key"),
            color_palette=c.get("color_palette", []),
        ))

    # 8. Save to session history (SQLite)
    session_service.append_history(
        body.session_id,
        body.prompt,
        sql,
        [c.title for c in charts],
    )

    # 9. Assemble Audit & Trust Metadata
    from app.models.response_models import AuditMetadata
    audit_data = AuditMetadata(
        sanitized_sql=telemetry.get("sanitized_sql", sql),
        execution_time_ms=telemetry.get("execution_time_ms", 0.0),
        rows_scanned=telemetry.get("rows_scanned", len(rows)),
        is_read_only=telemetry.get("is_read_only", True),
        confidence_score=0.98 if (verification_result and verification_result.verified) else 0.85,
        assumptions=[
            f"Query executed in read-only mode ({telemetry.get('rows_scanned', len(rows))} rows returned)",
            f"AST-validated against introspected schema with enforced limit of 1000",
        ],
        verification=verification_result,
    )

    return DashboardResponse(
        sql=telemetry.get("sanitized_sql", sql),
        dashboard_title=ai_response.get("dashboard_title", "Dashboard"),
        charts=charts,
        insight_summary=insight_summary,
        data_limitations=data_limitations,
        follow_up_suggestions=ai_response.get("follow_up_suggestions", []),
        audit=audit_data,
        error=None,
    )
