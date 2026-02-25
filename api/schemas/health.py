"""Health check response schema."""
from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """API health status and model readiness."""

    status: str = Field(..., examples=["healthy"])
    version: str = Field(..., examples=["1.0.0"])
    model_loaded: bool = Field(..., examples=[True])
    model_classes: int = Field(..., examples=[15])
    timestamp: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "1.0.0",
                    "model_loaded": True,
                    "model_classes": 15,
                    "timestamp": "2026-02-24T10:30:00Z",
                }
            ]
        }
    }
