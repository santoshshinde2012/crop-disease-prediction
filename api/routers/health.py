"""Health check endpoint."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from api.dependencies import get_predictor
from api.schemas.health import HealthResponse
from src.inference.predictor import DiseasePredictor

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns API health status, model readiness, and version info.",
)
def health_check(predictor: DiseasePredictor = Depends(get_predictor)):
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model_loaded=predictor.model is not None,
        model_classes=predictor.num_classes,
        timestamp=datetime.now(timezone.utc),
    )
