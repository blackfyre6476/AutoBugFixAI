from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict, Any, Optional


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Status of the backend service")
    service: str = Field(default="autofix-ai-backend", description="Service identifier")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    environment: str = Field(..., description="Deployment environment")
    components: Dict[str, Any] = Field(
        default_factory=dict,
        description="Health status of downstream sub-components (agents, docker sandbox, repository engine)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "autofix-ai-backend",
                "version": "0.1.0",
                "timestamp": "2026-09-28T22:50:00Z",
                "environment": "development",
                "components": {
                    "orchestrator": "ready",
                    "sandbox": "docker_available",
                    "repository": "ready"
                }
            }
        }
    )
