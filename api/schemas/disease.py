"""Disease library response schemas."""
from pydantic import BaseModel, Field


class DiseaseDetailResponse(BaseModel):
    """Full disease information including symptoms, treatment, and prevention."""

    name: str = Field(..., examples=["Tomato: Early Blight"])
    crop: str = Field(..., examples=["Tomato"])
    severity: str = Field(..., examples=["Moderate"])
    symptoms: list[str]
    treatment: str
    prevention: list[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Tomato: Early Blight",
                    "crop": "Tomato",
                    "severity": "Moderate",
                    "symptoms": [
                        "Concentric ring (target-like) dark brown spots on lower leaves",
                        "Leaves yellow around lesions and drop prematurely",
                        "Fruit may develop dark, leathery spots near the stem end",
                    ],
                    "treatment": "Apply chlorothalonil fungicide. Mulch around base to prevent spore splash.",
                    "prevention": [
                        "Stake plants for better air circulation",
                        "Apply mulch to prevent soil splash onto leaves",
                        "Remove infected lower leaves promptly",
                    ],
                }
            ]
        }
    }


class DiseaseListResponse(BaseModel):
    """List of all supported disease classes."""

    count: int = Field(..., examples=[15])
    diseases: list[DiseaseDetailResponse]
