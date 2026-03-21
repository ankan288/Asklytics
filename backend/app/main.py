import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database.sample_db import seed_database
from app.database.init_auth_tables import init_auth_tables
from app.routers import session, query, upload, auth, conversation
from app.middleware.auth import AuthMiddleware

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

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware (after CORS, before routes)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router)  # Auth endpoints (public)
app.include_router(conversation.router)  # Conversation history (protected)
app.include_router(session.router)
app.include_router(query.router)
app.include_router(upload.router)


@app.get("/health")
def health():
    return {"status": "ok"}

# Auto-reload trigger

# Reloading for new Groq API key
