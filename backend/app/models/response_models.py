from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class ChartSpec(BaseModel):
    id: str
    type: str  # line | bar | pie | area | kpi
    title: str
    data: List[Dict[str, Any]] = []
    x_key: Optional[str] = None
    y_keys: List[str] = []
    z_key: Optional[str] = None
    color_palette: List[str] = []


class ClaimItem(BaseModel):
    claim_text: str
    claimed_value: str
    matched_value: Optional[float] = None
    status: str  # VERIFIED | UNVERIFIED | CONTRADICTION
    explanation: str


class VerificationResult(BaseModel):
    verified: bool = True
    verification_rate: float = 1.0
    claims_total: int = 0
    claims_verified: int = 0
    claims_contradictions: int = 0
    claims_unverified: int = 0
    claims: List[ClaimItem] = []
    verified_summary: str = ""
    badge: str = ""


class ConsensusData(BaseModel):
    agreement_score: float = 1.0
    status: str = "CONSENSUS_REACHED"
    primary_model: str = "Gemini 2.0 Flash"
    secondary_model: Optional[str] = None
    differences: List[str] = []
    comparison_summary: str = ""


class AuditMetadata(BaseModel):
    sanitized_sql: Optional[str] = None
    execution_time_ms: float = 0.0
    rows_scanned: int = 0
    is_read_only: bool = True
    confidence_score: float = 0.95
    assumptions: List[str] = []
    chart_corrections: List[str] = []
    verification: Optional[VerificationResult] = None
    consensus: Optional[ConsensusData] = None


class ClarificationOption(BaseModel):
    label: str
    subtext: str
    refined_prompt: str


class ClarificationPayload(BaseModel):
    is_ambiguous: bool = True
    matched_term: str = ""
    question: str = ""
    options: List[ClarificationOption] = []


class DashboardResponse(BaseModel):
    sql: Optional[str] = None
    dashboard_title: str = ""
    charts: List[ChartSpec] = []
    insight_summary: str = ""
    data_limitations: Optional[str] = None
    follow_up_suggestions: List[str] = []
    audit: Optional[AuditMetadata] = None
    clarification: Optional[ClarificationPayload] = None
    error: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str


class UploadResponse(BaseModel):
    datasource_id: str
    table_name: str
    columns: Dict[str, str] = {}
