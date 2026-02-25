"""Custom exceptions and FastAPI exception handlers."""
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("api.exceptions")


class InvalidImageError(Exception):
    """Raised when the uploaded file cannot be opened as an image."""


class FileTooLargeError(Exception):
    """Raised when the uploaded file exceeds the maximum allowed size."""

    def __init__(self, actual_bytes: int, max_bytes: int):
        self.actual_mb = actual_bytes / (1024 * 1024)
        self.max_mb = max_bytes / (1024 * 1024)
        super().__init__(
            f"File size ({self.actual_mb:.1f} MB) exceeds limit ({self.max_mb:.1f} MB)"
        )


def _error_response(status_code: int, error_code: str, detail: str) -> JSONResponse:
    """Build a consistent JSON error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "detail": detail,
        },
    )


def register_exception_handlers(app: FastAPI):
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(InvalidImageError)
    async def invalid_image_handler(request: Request, exc: InvalidImageError):
        logger.warning("Invalid image upload on %s", request.url.path)
        return _error_response(
            status.HTTP_400_BAD_REQUEST,
            "INVALID_IMAGE",
            "The uploaded file could not be processed as an image. "
            "Please upload a valid JPEG or PNG file.",
        )

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(request: Request, exc: FileTooLargeError):
        logger.warning("Oversized file upload: %s", exc)
        return _error_response(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "FILE_TOO_LARGE",
            f"File size ({exc.actual_mb:.1f} MB) exceeds the maximum "
            f"allowed size ({exc.max_mb:.1f} MB).",
        )
