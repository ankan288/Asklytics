"""
Admin router - Protected endpoints requiring admin role and permissions.
"""
import os
import sqlite3
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel
from app.config import get_settings
from app.services.auth_service import AuthService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class UpdateRoleRequest(BaseModel):
    role: str  # "user" or "admin"


async def require_admin(request: Request) -> Dict[str, Any]:
    """
    Security Dependency: Validates JWT token and asserts user role is strictly 'admin'.
    Returns the authenticated admin user dict.
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        auth_header = request.headers.get("Authorization", "")
        token = AuthService.extract_token_from_header(auth_header)
        if token:
            user_id = AuthService.verify_token(token, token_type="access")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access admin resources.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService()
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user account not found.",
        )

    if user.get("role") != "admin":
        logger.warning(f"Unauthorized admin access attempt by user {user_id} ({user.get('email')})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin privileges required to access this endpoint.",
        )

    return user


@router.get("/stats")
async def get_admin_stats(admin_user: Dict = Depends(require_admin)):
    """Retrieve high-level system telemetry and platform usage metrics."""
    settings = get_settings()
    user_service = UserService()

    users_count = len(user_service.list_users(limit=1000))

    # Query active conversations and sessions
    sessions_count = 0
    conversations_count = 0
    db_size_bytes = 0

    if os.path.exists(settings.db_path):
        db_size_bytes = os.path.getsize(settings.db_path)
        try:
            conn = sqlite3.connect(settings.db_path)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM conversations")
            conversations_count = cur.fetchone()[0]
            conn.close()
        except Exception:
            pass

    return {
        "status": "operational",
        "total_registered_users": users_count,
        "active_sessions": sessions_count,
        "total_conversations": conversations_count,
        "database_size_kb": round(db_size_bytes / 1024, 2),
        "admin_email": admin_user["email"],
    }


@router.get("/users")
async def list_users(limit: int = 50, admin_user: Dict = Depends(require_admin)):
    """List users for administration. Passwords and secrets are omitted."""
    user_service = UserService()
    return user_service.list_users(limit=limit)


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    body: UpdateRoleRequest,
    admin_user: Dict = Depends(require_admin)
):
    """Elevate or demote user permissions (requires admin role)."""
    user_service = UserService()
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user_service.update_user_role(user_id, body.role)
        logger.info(f"Admin {admin_user['email']} updated role of user {user_id} to {body.role}")
        return {"status": "success", "user_id": user_id, "new_role": body.role}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/system")
async def get_system_health(admin_user: Dict = Depends(require_admin)):
    """
    Check system configuration.
    CRITICAL: API keys and JWT secrets are strictly masked and never exposed.
    """
    settings = get_settings()
    return {
        "environment": settings.environment,
        "database_engine": "SQLite" if not settings.use_postgres else "PostgreSQL",
        "gemini_api_configured": bool(settings.gemini_api_key),
        "groq_api_configured": bool(settings.groq_api_key),
        "jwt_algorithm": settings.jwt_algorithm,
        "cors_origin": settings.cors_origin,
        "api_keys_hidden": True,
    }

