"""
Authentication router - Login, signup, token refresh endpoints.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.models.auth_models import (
    SignUpRequest, LoginRequest, RefreshTokenRequest,
    TokenResponse, UserProfile, AuthResponse
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: SignUpRequest):
    """
    Register new user account.

    Args:
        request: {email: str, password: str}

    Returns:
        {user, access_token, refresh_token}

    Raises:
        409: Email already registered
        400: Invalid input
    """
    user_service = UserService()

    # Check if email already exists
    existing_user = user_service.get_user_by_email(request.email)
    if existing_user:
        logger.warning(f"Signup attempt with existing email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    try:
        # Hash password
        hashed_password = AuthService.hash_password(request.password)

        # Create user
        user_id = user_service.create_user(request.email, hashed_password)

        # Create session with tokens
        tokens = user_service.create_session(user_id)

        # Get user info (without password)
        user = user_service.get_user_by_id(user_id)

        return AuthResponse(
            user=UserProfile(
                id=user["user_id"],
                email=user["email"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            ),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=3600
        )

    except ValueError as e:
        logger.warning(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.

    Args:
        request: {email: str, password: str}

    Returns:
        {user, access_token, refresh_token}

    Raises:
        401: Invalid email or password
    """
    user_service = UserService()

    try:
        # Get user by email
        user = user_service.get_user_by_email(request.email)

        # Verify user exists and password is correct
        if not user or not AuthService.verify_password(request.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if account is active
        if not user.get("is_active", True):
            logger.warning(f"Login attempt on inactive account: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Update last_login
        user_service.update_last_login(user["user_id"])

        # Create new session with tokens
        tokens = user_service.create_session(user["user_id"])

        return AuthResponse(
            user=UserProfile(
                id=user["user_id"],
                email=user["email"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            ),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=3600
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.

    Args:
        request: {refresh_token: str}

    Returns:
        {access_token, token_type, expires_in}

    Raises:
        401: Invalid or expired refresh token
    """
    try:
        # Verify refresh token and get user_id
        user_id = AuthService.verify_token(request.refresh_token, token_type="refresh")

        # Generate new access token
        tokens = AuthService.refresh_access_token(request.refresh_token)

        return TokenResponse(**tokens)

    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout():
    """
    Logout user (client-side, just clear tokens).

    In JWT-based auth, logout is primarily client-side (delete tokens).
    This endpoint serves as a confirmation endpoint.
    """
    return {"status": "logged out", "message": "Please clear your tokens from local storage"}


@router.get("/me", response_model=UserProfile)
async def get_current_user(user_id: str):
    """
    Get current user info (requires valid access token in Authorization header).

    Args:
        user_id: From JWT token (injected by middleware)

    Returns:
        Current user info
    """
    user_service = UserService()

    try:
        user = user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserProfile(
            id=user["user_id"],
            email=user["email"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user"
        )
