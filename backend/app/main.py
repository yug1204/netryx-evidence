"""
NETRYX EVIDENCE — FastAPI Application Factory
AI-Powered Digital Evidence Intelligence & Investigation Platform.

Entry point: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.core.events import event_bus
from app.core.exceptions import NetryxException, netryx_to_http

# Import API routers
from app.api.v1.auth import router as auth_router
from app.api.v1.cases import router as cases_router
from app.api.v1.evidence import router as evidence_router

settings = get_settings()


# ── Lifespan ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    # Startup
    print("🚀 NETRYX EVIDENCE — Starting up...")
    await init_db()
    await event_bus.connect()
    print("✅ Database initialized")
    print("✅ Event bus connected")
    print(f"🌐 API running at http://localhost:8000{settings.API_PREFIX}")

    yield

    # Shutdown
    print("🛑 NETRYX EVIDENCE — Shutting down...")
    await event_bus.disconnect()
    await close_db()
    print("✅ Connections closed")


# ── Application ──────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Powered Digital Evidence Intelligence & Investigation Platform. "
        "From Evidence to Intelligence — Build for a Safer Digital India."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ──────────────────────────────────────
@app.exception_handler(NetryxException)
async def netryx_exception_handler(request: Request, exc: NetryxException):
    """Convert NETRYX domain exceptions to HTTP responses."""
    http_exc = netryx_to_http(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "code": "INTERNAL_ERROR",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# ── Register Routers ────────────────────────────────────────
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(cases_router, prefix=settings.API_PREFIX)
app.include_router(evidence_router, prefix=settings.API_PREFIX)

from app.api.v1.graph import router as graph_router
app.include_router(graph_router, prefix=settings.API_PREFIX)

from app.api.v1.chat import router as chat_router
app.include_router(chat_router, prefix=settings.API_PREFIX)


# ── Health Check ─────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and K8s probes."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — platform info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered Digital Evidence Intelligence & Investigation Platform",
        "tagline": "From Evidence to Intelligence",
        "docs": "/docs",
        "health": "/api/health",
    }
