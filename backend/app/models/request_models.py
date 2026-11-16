import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateSessionRequest(BaseModel):
    datasource_id: str = Field("default", min_length=1, max_length=100, description="Datasource identifier")

    @field_validator("datasource_id")
    @classmethod
    def validate_datasource_id(cls, v: str) -> str:
        cleaned = v.strip()
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", cleaned):
            raise ValueError("datasource_id may only contain alphanumeric characters, hyphens, and underscores")
        return cleaned


class QueryRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128, description="Session UUID")
    prompt: str = Field(..., min_length=2, max_length=2000, description="Natural language question")
    datasource_id: str = Field("default", min_length=1, max_length=100, description="Datasource identifier")
    skip_disambiguation: bool = False

    @field_validator("prompt")
    @classmethod
    def sanitize_and_validate_prompt(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Question must be at least 2 characters long")
        # Reject control characters or null bytes
        if "\x00" in cleaned or re.search(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", cleaned):
            raise ValueError("Question contains invalid control characters")
        return cleaned

    @field_validator("session_id", "datasource_id")
    @classmethod
    def sanitize_identifiers(cls, v: str) -> str:
        cleaned = v.strip()
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", cleaned):
            raise ValueError("Identifier contains invalid characters")
        return cleaned
