"""Prediction request/response schemas."""
from pydantic import BaseModel, Field


class TopKPrediction(BaseModel):
    """A single class prediction with its probability."""

    class_name: str = Field(..., examples=["Tomato: Early Blight"])
    confidence: float = Field(..., ge=0.0, le=1.0, examples=[0.87])


class PredictionResponse(BaseModel):
    """Complete prediction result for a leaf image."""

    success: bool = Field(True, examples=[True])
    prediction: str = Field(
        ...,
        description="Top predicted disease class",
        examples=["Tomato: Early Blight"],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the top prediction",
        examples=[0.9523],
    )
    crop: str = Field(
        ...,
        description="Crop type extracted from the prediction",
        examples=["Tomato"],
    )
    severity: str = Field(
        ...,
        description="Disease severity level",
        examples=["Moderate"],
    )
    treatment: str = Field(
        ...,
        description="Recommended treatment action",
        examples=[
            "Apply chlorothalonil fungicide. Mulch around base to prevent spore splash."
        ],
    )
    top_k: list[TopKPrediction] = Field(
        ...,
        description="Top-K predictions sorted by confidence (descending)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "prediction": "Tomato: Early Blight",
                    "confidence": 0.9523,
                    "crop": "Tomato",
                    "severity": "Moderate",
                    "treatment": "Apply chlorothalonil fungicide. Mulch around base to prevent spore splash.",
                    "top_k": [
                        {
                            "class_name": "Tomato: Early Blight",
                            "confidence": 0.9523,
                        },
                        {
                            "class_name": "Tomato: Late Blight",
                            "confidence": 0.0234,
                        },
                        {
                            "class_name": "Tomato: Septoria Leaf Spot",
                            "confidence": 0.0102,
                        },
                    ],
                }
            ]
        }
    }
