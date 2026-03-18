"""
Authentication middleware - Validates JWT tokens on protected routes.
Supports both Supabase tokens and backend-generated tokens.
"""
import logging
import jwt
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service import AuthService
from app.config import get_settings

logger = logging.getLogger(__name__)

# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/query",
    "/sessions",  # Fixed: was /session, but router uses /sessions
    "/upload",
    "/conversations",  # Temporarily public until Supabase auth is fully configured
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT token validation middleware.
    Validates Authorization header and injects user_id into request state.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and validate token if required.

        Token format: Authorization: Bearer {jwt_token}
        """
        # Skip auth for public routes (check if path starts with any public route)
        path = request.url.path
        for public_route in PUBLIC_ROUTES:
            if path == public_route or path.startswith(public_route + "/") or path.startswith(public_route + "?"):
                return await call_next(request)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get Authorization header
        auth_header = request.headers.get("Authorization", "")

        # Validate header format
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Missing or invalid auth header for {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token
        token = auth_header[7:]  # Remove "Bearer " prefix

        try:
            settings = get_settings()
            user_id = None

            # First try Supabase token format (doesn't require "type" field)
            try:
                payload = jwt.decode(
                    token,
                    settings.supabase_jwt_secret,
                    algorithms=[settings.jwt_algorithm],
                    options={"verify_aud": False}  # Supabase tokens may have different audience
                )
                user_id = payload.get("sub")
                if user_id:
                    logger.debug(f"✓ Authenticated via Supabase token: {user_id}")
                    request.state.user_id = user_id
                    response = await call_next(request)
                    return response
            except jwt.ExpiredSignatureError:
                logger.warning("Supabase token expired")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jwt.InvalidTokenError as e:
                logger.debug(f"Supabase token validation failed: {e}")
                pass  # Try backend format below

            # Fall back to backend token format (requires "type" field)
            user_id = AuthService.verify_token(token, token_type="access")

            if not user_id:
                logger.warning("Invalid token - could not extract user_id")
                raise ValueError("Invalid token format")

            # Inject user_id into request state
            request.state.user_id = user_id
            logger.debug(f"✓ Authenticated user: {user_id}")

        except ValueError as e:
            logger.warning(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )

        # Process request
        response = await call_next(request)
        return response


def get_current_user(request: Request) -> str:
    """
    Get current user_id from request state.

    Usage in route:
        @router.get("/conversations")
        async def get_conversations(user_id: str = Depends(get_current_user)):
            ...

    Args:
        request: FastAPI Request object

    Returns:
        user_id (from JWT token)

    Raises:
        HTTPException: If user_id not found in request state
    """
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        logger.error("user_id not found in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    return user_id
