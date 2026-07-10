import logging
import re
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


router = APIRouter()
logger = logging.getLogger(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

MIN_RESUME_LENGTH = 100
MAX_RESUME_LENGTH = 40_000

STANDARD_SECTION_HEADINGS = {
    "professional summary",
    "summary",
    "profile",
    "professional profile",
    "work experience",
    "professional experience",
    "experience",
    "employment history",
    "education",
    "technical skills",
    "skills",
    "core competencies",
    "projects",
    "personal projects",
    "academic projects",
    "certifications",
    "certificates",
    "languages",
    "achievements",
    "awards",
    "references",
}


# =========================================================
# REQUEST MODEL
# =========================================================

class ResumePdfRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    resume_text: str = Field(
        ...,
        min_length=MIN_RESUME_LENGTH,
        max_length=MAX_RESUME_LENGTH,
    )

    filename: str = Field(
        default="improved_resume.pdf",
        min_length=1,
        max_length=120,
    )


# =========================================================
# TEXT HELPERS
# =========================================================

def safe_pdf_filename(filename: str) -> str:
    filename = filename.strip()

    if filename.lower().endswith(".pdf"):
        filename = filename[:-4]

    filename = re.sub(
        r"[^a-zA-Z0-9._-]+",
        "_",
        filename,
    )

    filename = filename.strip("._-")

    if not filename:
        filename = "improved_resume"

    return f"{filename[:100]}.pdf"


def escape_reportlab_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def is_section_heading(line: str) -> bool:
    cleaned_line = line.strip().lower().rstrip(":")

    if cleaned_line in STANDARD_SECTION_HEADINGS:
        return True

    if (
        2 <= len(line.split()) <= 5
        and len(line) <= 60
        and line.isupper()
    ):
        return True

    return False


def is_bullet_line(line: str) -> bool:
    return bool(
        re.match(
            r"^\s*(?:[-*•●▪◦])\s+",
            line,
        )
    )


def clean_bullet_text(line: str) -> str:
    return re.sub(
        r"^\s*(?:[-*•●▪◦])\s+",
        "",
        line,
    ).strip()


# =========================================================
# PDF GENERATION
# =========================================================

def create_resume_pdf(resume_text: str) -> BytesIO:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Improved Resume",
        author="Resume Analyser",
    )

    sample_styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "ResumeName",
        parent=sample_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=5 * mm,
    )

    section_style = ParagraphStyle(
        "ResumeSection",
        parent=sample_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=sample_styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        spaceAfter=2 * mm,
    )

    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=body_style,
        leftIndent=5 * mm,
        firstLineIndent=-3 * mm,
        bulletIndent=2 * mm,
        spaceAfter=1.5 * mm,
    )

    story = []

    lines = [
        line.strip()
        for line in resume_text.splitlines()
    ]

    first_content_line = True

    for line in lines:
        if not line:
            story.append(Spacer(1, 1.5 * mm))
            continue

        safe_line = escape_reportlab_text(line)

        if first_content_line:
            story.append(
                Paragraph(
                    safe_line,
                    name_style,
                )
            )
            first_content_line = False
            continue

        if is_section_heading(line):
            story.append(
                Paragraph(
                    safe_line.upper(),
                    section_style,
                )
            )
            continue

        if is_bullet_line(line):
            bullet_text = escape_reportlab_text(
                clean_bullet_text(line)
            )

            story.append(
                Paragraph(
                    f"• {bullet_text}",
                    bullet_style,
                )
            )
            continue

        story.append(
            Paragraph(
                safe_line,
                body_style,
            )
        )

    if not story:
        raise ValueError(
            "The resume does not contain printable content"
        )

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# API ROUTE
# =========================================================

@router.post("/resume-pdf")
async def generate_resume_pdf(
    payload: ResumePdfRequest,
):
    try:
        pdf_buffer = create_resume_pdf(
            payload.resume_text
        )

        filename = safe_pdf_filename(
            payload.filename
        )

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                ),
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Unexpected error while generating resume PDF"
        )

        raise HTTPException(
            status_code=500,
            detail="Could not generate the PDF",
        )