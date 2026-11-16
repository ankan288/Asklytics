import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database.sample_db import seed_database
from app.database.init_auth_tables import init_auth_tables
from app.routers import session, query, upload, auth, conversation, admin
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting up — initializing databases...")
    seed_database(settings.db_path)
    init_auth_tables()
    logger.info("✅ All databases ready.")
    yield


app = FastAPI(
    title="Asklytics API",
    description="Conversational Analytics Platform - Turn questions into interactive dashboards",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()

# Add authentication middleware (checks token on all non-public routes)
app.add_middleware(AuthMiddleware)

# Add Rate Limiting middleware (sliding-window rate limiter)
app.add_middleware(RateLimitMiddleware)

# Add CORS middleware (added last so it is outermost and attaches headers to all responses including 401 and 429)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)          # Auth endpoints (register, login, me)
app.include_router(admin.router)         # Protected Admin endpoints (stats, users, role update)
app.include_router(conversation.router)  # Conversation history
app.include_router(session.router)       # Sessions
app.include_router(query.router)         # Natural language queries
app.include_router(upload.router)        # File uploads


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Asklytics Backend API",
        "message": "Backend API is running successfully!",
        "frontend_url": "http://localhost:3000",
        "dashboard_url": "http://localhost:3000/dashboard",
        "interactive_docs": "http://localhost:8000/docs",
        "health_check": "http://localhost:8000/health",
        "security": {
            "ast_sanitization": "sqlglot",
            "rate_limiting": "enabled",
            "secrets_redaction": "enabled"
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}
