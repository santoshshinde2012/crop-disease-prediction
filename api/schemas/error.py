"""Unified error response schema for consistent API error formatting."""
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error envelope returned by all error handlers."""

    success: bool = Field(False, examples=[False])
    error_code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["INVALID_IMAGE"],
    )
    detail: str = Field(
        ...,
        description="Human-readable error message",
        examples=["The uploaded file could not be processed as an image."],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error_code": "INVALID_IMAGE",
                    "detail": "The uploaded file could not be processed as an image. "
                    "Please upload a valid JPEG or PNG file.",
                }
            ]
        }
    }
