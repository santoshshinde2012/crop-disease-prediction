"""Disease library endpoints — reference data for all supported classes."""
from fastapi import APIRouter, HTTPException, Query, status

from api.schemas.disease import DiseaseDetailResponse, DiseaseListResponse
from api.schemas.error import ErrorResponse
from src.data.disease_info import DISEASE_DETAILS

router = APIRouter(tags=["Disease Library"])


@router.get(
    "/diseases",
    response_model=DiseaseListResponse,
    summary="List all disease classes",
    description=(
        "Returns all 15 supported crop disease classes with full details "
        "including symptoms, treatment, and prevention strategies. "
        "Optionally filter by crop name."
    ),
)
def list_diseases(
    crop: str | None = Query(
        None, description="Filter by crop name (Corn, Potato, Tomato)"
    ),
):
    diseases = []
    for name, details in DISEASE_DETAILS.items():
        if crop and details["crop"].lower() != crop.lower():
            continue
        diseases.append(DiseaseDetailResponse(name=name, **details))

    return DiseaseListResponse(count=len(diseases), diseases=diseases)


@router.get(
    "/diseases/{disease_name}",
    response_model=DiseaseDetailResponse,
    summary="Get disease details",
    description="Returns detailed information for a specific disease class.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Disease not found in supported classes",
        }
    },
)
def get_disease(disease_name: str):
    details = DISEASE_DETAILS.get(disease_name)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Disease '{disease_name}' not found. "
                "Use GET /api/v1/diseases to see all available classes."
            ),
        )
    return DiseaseDetailResponse(name=disease_name, **details)
