"""Health check endpoints — liveness, readiness, and detailed status."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from api.config import API_VERSION
from api.dependencies import get_predictor
from api.schemas.health import HealthResponse
from src.inference.predictor import DiseasePredictor

router = APIRouter(tags=["Health"])


@router.get(
    "/health/live",
    summary="Liveness probe",
    description="Returns 200 if the process is alive. Used by container orchestrators.",
)
def liveness():
    return {"status": "alive"}


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Readiness check",
    description="Returns API health status, model readiness, and version info.",
)
def health_check(predictor: DiseasePredictor = Depends(get_predictor)):
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        model_loaded=predictor.model is not None,
        model_classes=predictor.num_classes,
        timestamp=datetime.now(timezone.utc),
    )
