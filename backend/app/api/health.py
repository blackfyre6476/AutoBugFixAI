from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import sys
from app.core.config import Settings, get_settings
from models.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Get backend service health status")
@router.get("/api/v1/health", response_model=HealthResponse, summary="Get API v1 health status")
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Health check endpoint returning system status, timestamp, environment,
    and modular component status.
    """
    return HealthResponse(
        status="healthy",
        service="autofix-ai-backend",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.ENVIRONMENT,
        components={
            "python_version": sys.version.split()[0],
            "orchestrator": "idle",
            "sandbox": "ready",
            "repository": "ready",
            "agents": {
                "repository_analyst": "standby",
                "bug_investigator": "standby",
                "fix_generator": "standby",
                "validation_agent": "standby",
                "regression_agent": "standby",
            }
        }
    )
