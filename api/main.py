"""
Crop Disease Classification API

Usage: uvicorn api.main:app --reload
"""
import logging
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to sys.path so `from src.*` imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.inference.predictor import DiseasePredictor  # noqa: E402

from api.routers import diseases, health, prediction  # noqa: E402
from api.exceptions import register_exception_handlers  # noqa: E402

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")


# ── Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and verify ML model at startup; release at shutdown."""
    logger.info("Starting Crop Disease Classification API ...")
    try:
        predictor = DiseasePredictor()
        logger.info(
            "Model loaded: %d classes, checkpoint=%s",
            predictor.num_classes,
            predictor.model_path,
        )
        app.state.predictor = predictor
    except Exception:
        logger.critical("Failed to load model — aborting startup", exc_info=True)
        raise

    yield

    logger.info("Shutting down — releasing model resources ...")
    del app.state.predictor


# ── App factory ──────────────────────────────────────────────────
app = FastAPI(
    title="Crop Disease Classification API",
    description=(
        "AI-powered crop disease identification from leaf images.\n\n"
        "Upload a photo of a **Tomato**, **Potato**, or **Corn** leaf to get "
        "disease diagnosis with treatment recommendations.\n\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        "| Model | MobileNetV2 |\n"
        "| Accuracy | 97.8 % |\n"
        "| Classes | 15 |\n"
        "| Inference | ~9 ms (GPU) |"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Health",
            "description": "System health and model status checks.",
        },
        {
            "name": "Prediction",
            "description": (
                "Upload leaf images to get disease predictions "
                "with treatment recommendations."
            ),
        },
        {
            "name": "Disease Library",
            "description": (
                "Browse all 15 supported crop disease classes "
                "with symptoms, treatment, and prevention info."
            ),
        },
    ],
)


# ── Middleware ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with method, path, status, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.0f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ── Exception handlers ───────────────────────────────────────────
register_exception_handlers(app)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors — log and return 500."""
    logger.error("Unhandled exception on %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# ── Routers ──────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1")
app.include_router(prediction.router, prefix="/api/v1")
app.include_router(diseases.router, prefix="/api/v1")
