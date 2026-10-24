from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


# Temporary in-memory storage for brand profiles.
# Profiles will reset when the server restarts.
brand_profiles = {}


class BrandProfileCreate(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    required_terms: list[str] = Field(default_factory=list)
    forbidden_terms: list[str] = Field(default_factory=list)
    brand_voice: str = Field(
        default="professional",
        min_length=1,
        max_length=100,
    )


@router.get("/health", tags=["System"])
def health_check():
    """Check whether the TrueMark backend is running."""
    return {
        "status": "healthy",
        "application": "TrueMark AI",
        "message": "TrueMark backend is running",
    }


@router.get("/info", tags=["System"])
def application_info():
    """Return application information."""
    return {
        "name": "TrueMark AI",
        "version": "1.0.0",
        "description": (
            "AI-assisted brand consistency and content analysis platform"
        ),
        "features": [
            "Text-based brand consistency analysis",
            "Required brand term validation",
            "Forbidden brand term detection",
            "Structured analysis findings",
            "Brand profile management",
        ],
    }


@router.get("/features", tags=["System"])
def available_features():
    """List the analysis capabilities currently implemented."""
    return {
        "implemented": [
            {
                "id": "required_terms",
                "name": "Required Term Validation",
                "description": (
                    "Checks whether required brand words and phrases "
                    "appear in content."
                ),
            },
            {
                "id": "forbidden_terms",
                "name": "Forbidden Term Detection",
                "description": (
                    "Detects prohibited words and phrases in content."
                ),
            },
            {
                "id": "severity_assessment",
                "name": "Finding Severity",
                "description": "Classifies rule violations by severity.",
            },
            {
                "id": "brand_profiles",
                "name": "Brand Profile Management",
                "description": (
                    "Creates and retrieves brand profiles with "
                    "required terms, forbidden terms, and brand voice."
                ),
            },
        ],
        "planned": [
            "Document and image analysis",
            "Analysis history and reports",
            "AI-assisted recommendations",
        ],
    }


@router.post("/brands", tags=["Brand Profiles"], status_code=201)
def create_brand_profile(profile: BrandProfileCreate):
    """Create a brand profile."""
    brand_id = str(uuid4())

    saved_profile = {
        "id": brand_id,
        **profile.model_dump(),
    }

    brand_profiles[brand_id] = saved_profile

    return {
        "status": "success",
        "message": "Brand profile created successfully.",
        "profile": saved_profile,
    }


@router.get("/brands", tags=["Brand Profiles"])
def list_brand_profiles():
    """List all brand profiles created during this server session."""
    return {
        "count": len(brand_profiles),
        "profiles": list(brand_profiles.values()),
    }


@router.get("/brands/{brand_id}", tags=["Brand Profiles"])
def get_brand_profile(brand_id: str):
    """Retrieve a brand profile by its ID."""
    profile = brand_profiles.get(brand_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Brand profile not found.",
        )

    return profile