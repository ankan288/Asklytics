"""
Asklytics API Rate Limiting Middleware.
Provides in-memory sliding window rate limiting per client IP to prevent DoS,
brute-force attacks, and token quota exhaustion.
"""
import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Specific limits (max requests, window in seconds) per path prefix
ROUTE_LIMITS = {
    "/query": (20, 60),            # 20 requests per minute for LLM natural language queries
    "/upload": (10, 60),           # 10 CSV uploads per minute
    "/auth/login": (10, 60),       # 10 login attempts per minute (brute force protection)
    "/auth/register": (10, 60),    # 10 registrations per minute
    "/admin": (30, 60),            # 30 admin actions per minute
}
DEFAULT_LIMIT = (120, 60)          # 120 requests per minute for general endpoints


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # client_ip -> route_key -> list of request timestamps
        self.history = defaultdict(lambda: defaultdict(list))

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP handling forward headers if behind a reverse proxy."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "127.0.0.1"

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for CORS preflight, static docs, and health checks
        path = request.url.path
        if request.method == "OPTIONS" or path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        now = time.time()

        # Determine limit for this route
        max_requests, window_secs = DEFAULT_LIMIT
        matched_prefix = "default"
        for route_prefix, limit in ROUTE_LIMITS.items():
            if path.startswith(route_prefix):
                max_requests, window_secs = limit
                matched_prefix = route_prefix
                break

        # Prune expired timestamps in the sliding window
        window_start = now - window_secs
        timestamps = self.history[client_ip][matched_prefix]
        self.history[client_ip][matched_prefix] = [t for t in timestamps if t > window_start]
        current_count = len(self.history[client_ip][matched_prefix])

        if current_count >= max_requests:
            retry_after = int(window_secs - (now - self.history[client_ip][matched_prefix][0])) + 1
            logger.warning(f"Rate limit exceeded for {client_ip} on {path} ({current_count}/{max_requests})")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Maximum {max_requests} requests per {window_secs} seconds allowed for this endpoint.",
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(max_after := max(1, retry_after)),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Record this request
        self.history[client_ip][matched_prefix].append(now)

        response = await call_next(request)
        remaining = max(0, max_requests - (current_count + 1))
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

