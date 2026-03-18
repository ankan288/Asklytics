from pydantic import BaseModel
from typing import Optional


class CreateSessionRequest(BaseModel):
    datasource_id: str = "default"


class QueryRequest(BaseModel):
    session_id: str
    prompt: str
    datasource_id: str = "default"
