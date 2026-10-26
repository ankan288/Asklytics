import logging
from fastapi import APIRouter, HTTPException
from app.models.request_models import QueryRequest
from app.models.response_models import (
    DashboardResponse,
    ChartSpec,
    ClarificationPayload,
    VerificationResult,
    AuditMetadata,
    ConsensusData,
)
from app.services import (
    session_service,
    schema_service,
    gemini_service,
    sql_service,
    ambiguity_service,
    chart_validator,
    state_manager,
    semantic_layer,
    consensus_service,
    claim_verifier,
)
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

    # 2. Check for underspecified / ambiguous queries (Upgrade #2 Ambiguity Chips)
    if not body.skip_disambiguation:
        ambiguity_data = ambiguity_service.check_ambiguity(body.prompt)
        if ambiguity_data:
            return DashboardResponse(
                dashboard_title="Clarification Needed",
                insight_summary=ambiguity_data["question"],
                clarification=ClarificationPayload(**ambiguity_data),
                follow_up_suggestions=[opt["label"] for opt in ambiguity_data["options"]],
            )

    # 3. Get history, schema, structured analytical state, and semantic definitions
    history = session_service.get_history(body.session_id)
    try:
        schema = schema_service.get_compact_schema(body.datasource_id)
    except ValueError as e:
        if body.datasource_id != "default":
            return DashboardResponse(
                error="This dataset is no longer available in memory (the dev server may have restarted). Please re-upload your CSV file."
            )
        return DashboardResponse(error=str(e))

    # Enrich prompt with multi-turn state (Upgrade #5) and semantic standards (Upgrade #8)
    state_ctx = state_manager.build_state_prompt_context(body.session_id)
    semantic_ctx = semantic_layer.format_semantic_prompt_context()
    enriched_prompt = body.prompt
    if state_ctx or semantic_ctx:
        enriched_prompt = f"{body.prompt}\n{state_ctx}\n{semantic_ctx}"

    # 4. Stage 1 — generate SQL + chart specs (no insight yet)
    try:
        ai_response = gemini_service.generate_dashboard(schema, enriched_prompt, history)
    except ValueError as e:
        return DashboardResponse(error=str(e))
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return DashboardResponse(error=f"AI service unavailable. Details: {str(e)}")

    # Handle AI "cannot answer" response
    if "error" in ai_response and len(ai_response) == 1:
        return DashboardResponse(error=ai_response["error"])

    # 5. Execute SQL against the real database with AST safety & telemetry (Upgrade #4)
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
    insight_summary = ""
    data_limitations = None
    try:
        insight = gemini_service.generate_insight(body.prompt, sql, rows)
        insight_summary = insight.get("insight_summary", "")
        data_limitations = insight.get("data_limitations")
    except Exception as e:
        logger.warning(f"Insight generation failed (non-fatal): {e}")

    # 6b. Verification Engine — evaluate numerical claims against real rows (Upgrade #1)
    verification_result = None
    try:
        raw_verification = claim_verifier.verify_insight(insight_summary, rows, sql)
        verification_result = VerificationResult(**raw_verification)
    except Exception as e:
        logger.warning(f"Claim verification failed (non-fatal): {e}")

    # 7. Cross-Model Consensus Analysis (Upgrade #3)
    consensus_res = consensus_service.compare_sql_semantics(sql)
    consensus_data = ConsensusData(**consensus_res.model_dump())

    # 8. VisEval Deterministic Chart Validation (Upgrade #6)
    raw_charts = ai_response.get("charts", [])
    sanitized_charts_raw, chart_corrections = chart_validator.validate_and_sanitize_charts(raw_charts, rows)
    charts = [
        ChartSpec(
            id=c.get("id", f"chart-{i+1}"),
            type=c.get("type", "bar"),
            title=c.get("title", ""),
            data=c.get("data", rows),
            x_key=c.get("x_key"),
            y_keys=c.get("y_keys", []),
            z_key=c.get("z_key"),
            color_palette=c.get("color_palette", []),
        )
        for i, c in enumerate(sanitized_charts_raw)
    ]

    # 9. Update multi-turn state (Upgrade #5) & session history
    state_manager.update_state_from_turn(body.session_id, body.prompt, sql)
    session_service.append_history(
        body.session_id,
        body.prompt,
        sql,
        [c.title for c in charts],
    )

    # 10. Assemble Audit & Trust Metadata (Upgrade #7)
    ast_meta = telemetry.get("ast_metadata", {})
    dynamic_assumptions = []
    if ast_meta.get("is_aggregate"):
        dynamic_assumptions.append("Aggregated metrics across transaction records")
    if ast_meta.get("has_group_by"):
        dynamic_assumptions.append("Grouped results by categorical business dimensions")
    if ast_meta.get("has_order_by"):
        dynamic_assumptions.append("Applied deterministic sorting to surface primary rankings")
    if ast_meta.get("has_with_cte"):
        dynamic_assumptions.append("Synthesized query using Common Table Expressions (CTE)")
    if len(rows) >= 1000:
        dynamic_assumptions.append("Query reached enforced safety ceiling of 1,000 rows")
    else:
        dynamic_assumptions.append(f"Complete result set bounded to {len(rows)} rows")
    dynamic_assumptions.append("Kernel-level read-only driver enforced")
    for corr in chart_corrections:
        dynamic_assumptions.append(corr)

    # Dynamic confidence score: 50% verification rate + 25% AST + 15% rows returned + 10% no contradictions
    v_rate = verification_result.verification_rate if verification_result else 1.0
    has_contradiction = bool(verification_result and getattr(verification_result, "claims_contradictions", 0) > 0)
    confidence = (0.50 * v_rate) + 0.25 + (0.15 if rows else 0.05) + (0.0 if has_contradiction else 0.10)
    dynamic_confidence = round(max(0.10, min(0.99, confidence)), 2)

    audit_data = AuditMetadata(
        sanitized_sql=telemetry.get("sanitized_sql", sql),
        execution_time_ms=telemetry.get("execution_time_ms", 0.0),
        rows_scanned=telemetry.get("rows_scanned", len(rows)),
        is_read_only=telemetry.get("is_read_only", True),
        confidence_score=dynamic_confidence,
        assumptions=dynamic_assumptions,
        chart_corrections=chart_corrections,
        verification=verification_result,
        consensus=consensus_data,
    )

    return DashboardResponse(
        sql=telemetry.get("sanitized_sql", sql),
        dashboard_title=ai_response.get("dashboard_title", "Dashboard"),
        charts=charts,
        insight_summary=insight_summary,
        data_limitations=data_limitations,
        follow_up_suggestions=ai_response.get("follow_up_suggestions", []),
        audit=audit_data,
        clarification=None,
        error=None,
    )
