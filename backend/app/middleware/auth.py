"""
Authentication middleware - Validates JWT tokens on protected routes.
Supports both Supabase tokens and backend-generated tokens.
"""
import logging
import jwt
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.services.auth_service import AuthService
from app.config import get_settings

logger = logging.getLogger(__name__)

# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/",
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
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
            if path == public_route or (public_route != "/" and path.startswith(public_route + "/")) or path.startswith(public_route + "?"):
                return await call_next(request)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get Authorization header
        auth_header = request.headers.get("Authorization", "")

        # Validate header format
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Missing or invalid auth header for {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required. Please log in to continue."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token
        token = auth_header[7:].strip()  # Remove "Bearer " prefix

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
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token expired. Please log in again."},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jwt.InvalidTokenError as e:
                logger.debug(f"Supabase token validation failed: {e}")
                pass  # Try backend format below

            # Fall back to backend token format (requires "type" field)
            user_id = AuthService.verify_token(token, token_type="access")

            if not user_id:
                logger.warning("Invalid token - could not extract user_id")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired token. Please log in again."},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Inject user_id into request state
            request.state.user_id = user_id
            logger.debug(f"✓ Authenticated user: {user_id}")

        except ValueError as e:
            logger.warning(f"Token validation failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed. Please log in again."},
                headers={"WWW-Authenticate": "Bearer"},
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
