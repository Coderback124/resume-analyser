import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.resume_improver import (
    ResumeImproverConfigurationError,
    ResumeImproverError,
    ResumeImproverResponseError,
    improve_resume,
)


router = APIRouter()
logger = logging.getLogger(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

MIN_RESUME_LENGTH = 100
MAX_RESUME_LENGTH = 40_000
MAX_JOB_DESCRIPTION_LENGTH = 30_000
MAX_FEEDBACK_ITEMS = 12
MAX_FEEDBACK_ITEM_LENGTH = 500


# =========================================================
# REQUEST MODEL
# =========================================================

class ImproveResumeRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    original_resume: str = Field(
        ...,
        min_length=MIN_RESUME_LENGTH,
        max_length=MAX_RESUME_LENGTH,
    )

    job_description: str = Field(
        default="",
        max_length=MAX_JOB_DESCRIPTION_LENGTH,
    )

    feedback: list[str] = Field(
        default_factory=list,
        max_length=MAX_FEEDBACK_ITEMS,
    )

    @field_validator("feedback")
    @classmethod
    def validate_feedback(
        cls,
        value: list[str],
    ) -> list[str]:

        cleaned_feedback = []

        for item in value:
            if not isinstance(item, str):
                continue

            cleaned_item = item.strip()

            if not cleaned_item:
                continue

            if len(cleaned_item) > MAX_FEEDBACK_ITEM_LENGTH:
                cleaned_item = cleaned_item[
                    :MAX_FEEDBACK_ITEM_LENGTH
                ]

            if cleaned_item not in cleaned_feedback:
                cleaned_feedback.append(cleaned_item)

        return cleaned_feedback


# =========================================================
# RESPONSE MODEL
# =========================================================

class ImproveResumeResponse(BaseModel):
    improved_resume: str
    original_resume: str
    improvement_count: int
    message: str


# =========================================================
# HELPERS
# =========================================================

def estimate_improvement_count(
    original_resume: str,
    improved_resume: str,
    feedback: list[str],
) -> int:
    """
    Returns a conservative UI-friendly estimate.

    This does not claim that every textual difference is a separate
    improvement. It uses supplied analysis feedback and whether the
    generated document differs meaningfully from the original.
    """

    if original_resume.strip() == improved_resume.strip():
        return 0

    if feedback:
        return min(len(feedback), MAX_FEEDBACK_ITEMS)

    return 1


# =========================================================
# API ROUTE
# =========================================================

@router.post(
    "/improve-resume",
    response_model=ImproveResumeResponse,
)
async def improve_resume_endpoint(
    payload: ImproveResumeRequest,
):
    try:
        improved_text = await improve_resume(
            original_resume=payload.original_resume,
            job_description=payload.job_description,
            feedback=payload.feedback,
        )

        improvement_count = estimate_improvement_count(
            original_resume=payload.original_resume,
            improved_resume=improved_text,
            feedback=payload.feedback,
        )

        return ImproveResumeResponse(
            improved_resume=improved_text,
            original_resume=payload.original_resume,
            improvement_count=improvement_count,
            message="Improved resume generated successfully",
        )

    except ResumeImproverConfigurationError:
        logger.error(
            "Resume improvement service is not configured"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Resume improvement is temporarily unavailable"
            ),
        )

    except ResumeImproverResponseError:
        logger.warning(
            "Resume improvement service returned an invalid response"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "The resume improvement service returned "
                "an incomplete response"
            ),
        )

    except ResumeImproverError as exc:
        logger.warning(
            "Resume improvement failed: %s",
            str(exc),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "The resume could not be improved at this time"
            ),
        )

    except Exception:
        logger.exception(
            "Unexpected error while improving resume"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )