"""Prediction endpoint — upload a leaf image to get disease diagnosis."""
import logging
import time
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from PIL import Image, UnidentifiedImageError

from api.config import ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE_MB
from api.dependencies import get_predictor
from api.exceptions import FileTooLargeError, InvalidImageError
from api.schemas.error import ErrorResponse
from api.schemas.prediction import PredictionResponse, TopKPrediction
from src.data.disease_info import DISEASE_DETAILS
from src.inference.predictor import DiseasePredictor

logger = logging.getLogger("api.prediction")

router = APIRouter(tags=["Prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict crop disease from leaf image",
    description=(
        "Upload a JPEG or PNG image of a Tomato, Potato, or Corn leaf. "
        "Returns the predicted disease class, confidence score, "
        "top-K alternative predictions, and treatment recommendations."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image file"},
        413: {"model": ErrorResponse, "description": "File exceeds 10 MB limit"},
        422: {"model": ErrorResponse, "description": "Unsupported file type"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
)
def predict_disease(
    file: UploadFile = File(..., description="Leaf image (JPEG or PNG, max 10 MB)"),
    top_k: int = Query(
        5, ge=1, le=15, description="Number of top predictions to return"
    ),
    predictor: DiseasePredictor = Depends(get_predictor),
):
    # ── Validate content type ────────────────────────────────────
    content_type = file.content_type or "unknown"
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Unsupported file type '{content_type}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            ),
        )

    # ── Read and validate file size ──────────────────────────────
    contents = file.file.read()
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise FileTooLargeError(len(contents), max_bytes)

    # ── Open and validate image ──────────────────────────────────
    try:
        image = Image.open(BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise InvalidImageError()
    except (OSError, ValueError):
        raise InvalidImageError()

    # ── Run prediction ───────────────────────────────────────────
    start = time.perf_counter()
    result = predictor.predict(image, top_k=top_k)
    inference_ms = (time.perf_counter() - start) * 1000

    disease_name = result["top_class"]
    details = DISEASE_DETAILS.get(disease_name, {})

    logger.info(
        "Prediction: %s (%.1f%%) in %.0f ms",
        disease_name,
        result["confidence"] * 100,
        inference_ms,
    )

    return PredictionResponse(
        success=True,
        prediction=disease_name,
        confidence=result["confidence"],
        crop=details.get("crop", disease_name.split(":")[0].strip()),
        severity=details.get("severity", "Unknown"),
        treatment=result["recommendation"],
        top_k=[
            TopKPrediction(class_name=cls, confidence=prob)
            for cls, prob in result["top_k_probs"].items()
        ],
    )
