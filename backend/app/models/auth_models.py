"""
Asklytics: Pydantic models for authentication and conversation management.
Complete Supabase-integrated schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# ============================================================================
# AUTHENTICATION REQUEST MODELS
# ============================================================================

class SignUpRequest(BaseModel):
    """User signup request (email + password + optional name)."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@asklytics.com",
                "password": "SecurePassword123",
                "full_name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """User login request (email + password)."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@asklytics.com",
                "password": "SecurePassword123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


# ============================================================================
# USER RESPONSE MODELS
# ============================================================================

class UserProfile(BaseModel):
    """User profile information (no password)."""
    id: str  # UUID as string for flexibility
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@asklytics.com",
                "full_name": "John Doe",
                "avatar_url": "https://...",
                "created_at": "2026-03-17T10:00:00",
                "last_login": "2026-03-17T10:15:00"
            }
        }


class UserProfileUpdate(BaseModel):
    """User profile update request."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response after login/signup."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds (1 hour)


class AuthResponse(BaseModel):
    """Full authentication response with user and tokens."""
    user: UserProfile
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


# ============================================================================
# CONVERSATION MODELS
# ============================================================================

class ConversationTurnCreate(BaseModel):
    """Add a turn to a conversation."""
    user_prompt: str
    sql_generated: Optional[str] = None
    charts: Optional[dict] = None
    insight_summary: Optional[str] = None
    data_limitations: Optional[str] = None
    execution_time_ms: Optional[int] = None


class ConversationTurn(BaseModel):
    """Conversation turn with all details."""
    id: int
    conversation_id: UUID
    turn_number: int
    user_prompt: str
    sql_generated: Optional[str] = None
    charts: Optional[dict] = None
    insight_summary: Optional[str] = None
    data_limitations: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreateRequest(BaseModel):
    """Create a new conversation."""
    title: Optional[str] = None
    datasource_id: str = "default"


class Conversation(BaseModel):
    """Full conversation with all turns."""
    id: UUID
    user_id: UUID
    title: Optional[str] = None
    datasource_id: str
    created_at: datetime
    updated_at: datetime
    turns: List[ConversationTurn] = []

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    """Conversation summary for list view."""
    id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    turn_count: int = 0


# ============================================================================
# INTERNAL JWT MODELS
# ============================================================================

class TokenPayload(BaseModel):
    """JWT token payload (internal use)."""
    sub: str  # user_id (UUID as string)
    type: str  # "access" or "refresh"
    iat: int  # issued at (unix timestamp)
    exp: int  # expiration (unix timestamp)


class JWTData(BaseModel):
    """Decoded JWT data."""
    user_id: str  # UUID as string
    token_type: str  # "access" or "refresh"


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    field: str
    message: str


class ValidationError(BaseModel):
    """Validation error response."""
    error: str = "Validation Error"
    details: List[ValidationErrorDetail]
