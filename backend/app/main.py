from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.health import router as health_router
from app.api.fixes import router as fixes_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Autonomous AI Bug Fixing Assistant API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(fixes_router)


@app.get("/", summary="Root status endpoint")
async def root():
    return {
        "message": "Welcome to AutoFix AI API - Autonomous AI Bug Fixing Assistant",
        "docs": "/docs",
        "health": "/api/v1/health",
        "version": settings.VERSION,
    }
