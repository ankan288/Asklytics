"""
Security utilities - Redacting secrets, sanitizing error messages, and input validation.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Patterns matching sensitive keys and tokens
SECRET_PATTERNS = [
    re.compile(r"AQ\.[A-Za-z0-9_-]{20,}", re.IGNORECASE),          # Gemini / Google OAuth style
    re.compile(r"AIza[0-9A-Za-z-_]{35}", re.IGNORECASE),           # Google AI API Keys
    re.compile(r"gsk_[A-Za-z0-9]{20,}", re.IGNORECASE),            # Groq API Keys
    re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.IGNORECASE),           # OpenAI / generic secret keys
    re.compile(r"Bearer\s+[A-Za-z0-9\-_.]+", re.IGNORECASE),       # Bearer JWT tokens
    re.compile(r"eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+"), # Raw JWT format
    re.compile(r"[A-Za-z]:\\[\w\\\.\-]+", re.IGNORECASE),          # Windows file paths
    re.compile(r"/[\w/\.\-]+/backend/[\w/\.\-]+", re.IGNORECASE),  # POSIX backend paths
]


def sanitize_error_message(error_str: str) -> str:
    """
    Scrub any API keys, credentials, JWTs, or server filesystem paths from error messages.
    Ensures zero leakage to the client or public API consumers.
    """
    if not error_str:
        return "An internal server error occurred."

    sanitized = str(error_str)
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED_CREDENTIAL]", sanitized)

    # If the error looks like an internal stack trace or raw API response, return a clean generic message
    if "Traceback" in sanitized or "Internal server" in sanitized or "sqlite3.OperationalError" in sanitized:
        logger.warning(f"Intercepted sensitive error detail: {sanitized}")
        return "A database or processing error occurred while fulfilling the request."

    return sanitized

