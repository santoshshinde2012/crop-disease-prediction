"""FastAPI dependency injection functions."""
import logging

from fastapi import HTTPException, Request, status

from src.inference.predictor import DiseasePredictor

logger = logging.getLogger("api.dependencies")


def get_predictor(request: Request) -> DiseasePredictor:
    """Retrieve the DiseasePredictor instance loaded during app startup."""
    predictor = getattr(request.app.state, "predictor", None)
    if predictor is None:
        logger.error("Prediction requested but model is not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. The service is starting up or encountered an error.",
        )
    return predictor
