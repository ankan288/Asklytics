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


class DashboardResponse(BaseModel):
    sql: Optional[str] = None
    dashboard_title: str = ""
    charts: List[ChartSpec] = []
    insight_summary: str = ""
    data_limitations: Optional[str] = None
    follow_up_suggestions: List[str] = []
    error: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str


class UploadResponse(BaseModel):
    datasource_id: str
    table_name: str
    columns: Dict[str, str] = {}
