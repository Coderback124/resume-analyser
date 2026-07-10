import logging
from typing import Optional

from openai import AsyncOpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL


logger = logging.getLogger(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

MAX_RESUME_LENGTH = 40_000
MAX_JOB_DESCRIPTION_LENGTH = 30_000
MAX_FEEDBACK_ITEMS = 12

MODEL_NAME = OPENAI_MODEL


# =========================================================
# CUSTOM EXCEPTIONS
# =========================================================

class ResumeImproverError(Exception):
    """Base exception for resume improvement failures."""


class ResumeImproverConfigurationError(ResumeImproverError):
    """Raised when the AI service is not configured correctly."""


class ResumeImproverResponseError(ResumeImproverError):
    """Raised when the AI service returns an unusable response."""


# =========================================================
# CLIENT
# =========================================================

def get_openai_client() -> AsyncOpenAI:
    if not OPENAI_API_KEY:
        raise ResumeImproverConfigurationError(
            "The resume improvement service is not configured"
        )

    return AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        timeout=45.0,
        max_retries=2,
    )


# =========================================================
# INPUT HELPERS
# =========================================================

def clean_text(
    value: Optional[str],
    max_length: int,
) -> str:
    if not value:
        return ""

    return value.strip()[:max_length]


def clean_feedback(
    feedback: Optional[list[str]],
) -> list[str]:
    if not feedback:
        return []

    cleaned_items = []

    for item in feedback[:MAX_FEEDBACK_ITEMS]:
        if not isinstance(item, str):
            continue

        cleaned_item = item.strip()

        if cleaned_item and cleaned_item not in cleaned_items:
            cleaned_items.append(cleaned_item[:500])

    return cleaned_items


def format_feedback(feedback: list[str]) -> str:
    if not feedback:
        return "No specific feedback was supplied."

    return "\n".join(
        f"- {item}"
        for item in feedback
    )


# =========================================================
# SYSTEM INSTRUCTIONS
# =========================================================

SYSTEM_INSTRUCTIONS = """
You are a professional resume editor.

Your task is to improve an existing resume using only facts that are
already present in the original resume.

STRICT FACTUAL ACCURACY RULES:

1. Never invent employment history.
2. Never invent employers.
3. Never invent job titles.
4. Never invent education.
5. Never invent qualifications.
6. Never invent certifications.
7. Never invent dates.
8. Never invent years of experience.
9. Never invent projects.
10. Never invent technical skills.
11. Never invent languages.
12. Never invent achievements.
13. Never invent numbers, percentages, metrics, or business results.
14. Never claim that the candidate has a requirement from the job
    description unless the original resume already proves it.
15. Never change contact details.
16. Never remove important factual information.

You may:

- improve grammar and clarity;
- improve professional wording;
- use stronger action-oriented language where factually supported;
- reorganise existing information;
- use standard ATS-friendly section headings;
- improve readability;
- make existing relevant skills easier to find;
- tailor emphasis toward the job description;
- incorporate job-description terminology only when it accurately
  describes experience or skills already present in the resume.

If the analysis recommends adding measurable results but the original
resume contains no real measurements, do not invent measurements.
Improve the wording without creating numbers.

If the job description asks for a skill that is absent from the
original resume, do not add that skill.

OUTPUT RULES:

Return only the complete improved resume.

Do not include:
- markdown code fences;
- explanations before the resume;
- explanations after the resume;
- analysis notes;
- a list of changes;
- statements such as "Here is your improved resume".

Use plain text with clear section headings and readable spacing.
Preserve the candidate's identity and all factual information.
"""


# =========================================================
# PROMPT BUILDER
# =========================================================

def build_improvement_prompt(
    original_resume: str,
    job_description: str,
    feedback: list[str],
) -> str:

    feedback_text = format_feedback(feedback)

    job_section = (
        job_description
        if job_description
        else "No job description was supplied."
    )

    return f"""
Improve the resume below.

Use the analysis feedback to guide the improvements.

If a job description is provided, tailor the resume toward it only
where the original resume already supports the relevant experience,
skills, or knowledge.

ANALYSIS FEEDBACK:
{feedback_text}

JOB DESCRIPTION:
{job_section}

ORIGINAL RESUME:
{original_resume}

Return only the complete improved resume in plain text.
"""


# =========================================================
# RESPONSE VALIDATION
# =========================================================

def validate_improved_resume(
    original_resume: str,
    improved_resume: str,
) -> str:

    cleaned_result = improved_resume.strip()

    if not cleaned_result:
        raise ResumeImproverResponseError(
            "The AI service returned an empty resume"
        )

    if len(cleaned_result) < 100:
        raise ResumeImproverResponseError(
            "The AI service returned an incomplete resume"
        )

    original_words = len(original_resume.split())
    improved_words = len(cleaned_result.split())

    if original_words >= 100:
        minimum_expected_words = max(
            80,
            int(original_words * 0.40),
        )

        if improved_words < minimum_expected_words:
            raise ResumeImproverResponseError(
                "The improved resume appears incomplete"
            )

    return cleaned_result


# =========================================================
# RESUME IMPROVEMENT SERVICE
# =========================================================

async def improve_resume(
    original_resume: str,
    job_description: str = "",
    feedback: Optional[list[str]] = None,
) -> str:

    clean_resume = clean_text(
        original_resume,
        MAX_RESUME_LENGTH,
    )

    clean_job_description = clean_text(
        job_description,
        MAX_JOB_DESCRIPTION_LENGTH,
    )

    clean_feedback_items = clean_feedback(feedback)

    if len(clean_resume) < 100:
        raise ResumeImproverError(
            "The original resume does not contain enough readable text"
        )

    prompt = build_improvement_prompt(
        original_resume=clean_resume,
        job_description=clean_job_description,
        feedback=clean_feedback_items,
    )

    client = get_openai_client()

    try:
        response = await client.responses.create(
            model=MODEL_NAME,
            instructions=SYSTEM_INSTRUCTIONS,
            input=prompt,
            max_output_tokens=5000,
        )

        improved_resume = response.output_text

        return validate_improved_resume(
            original_resume=clean_resume,
            improved_resume=improved_resume,
        )

    except ResumeImproverError:
        raise

    except Exception as exc:
        logger.exception(
            "OpenAI resume improvement request failed"
        )

        raise ResumeImproverError(
            "The resume could not be improved at this time"
        ) from exc