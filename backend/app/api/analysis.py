import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.core.models.services.analyzer_service import analyze_content


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["Brand Analysis"],
)


class AnalysisRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=50000,
        description="Content to analyze for brand consistency",
    )

    required_terms: list[str] = Field(
        default_factory=list,
        description="Words or phrases that must appear in the content",
    )

    forbidden_terms: list[str] = Field(
        default_factory=list,
        description="Words or phrases that must not appear in the content",
    )


@router.post("/text")
def analyze_text(request: AnalysisRequest):
    try:
        result = analyze_content(
            text=request.text,
            required_terms=request.required_terms,
            forbidden_terms=request.forbidden_terms,
        )

        return {
            "status": "success",
            "analysis_type": "truemark_analyzer_pipeline",
            "result": result,
        }

    except Exception as exc:
        logger.exception("Text analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Text analysis failed. Please check the backend logs.",
        ) from exc