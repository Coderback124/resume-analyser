from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from io import BytesIO
import logging
import re

from docx import Document
from PyPDF2 import PdfReader

router = APIRouter()
logger = logging.getLogger(__name__)

# 🔒 CONFIG
ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_SCORE = 6


# -------------------------------
# 📄 TEXT EXTRACTION
# -------------------------------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        return " ".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(BytesIO(file_bytes))
        return " ".join([p.text for p in doc.paragraphs])
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"TXT extraction error: {e}")
        return ""


# -------------------------------
# 🧠 CV ANALYSIS
# -------------------------------

def analyse_cv(text: str):
    text = text.lower()
    score = 0
    feedback = []

    checks = {
        "experience": "Add a work experience section",
        "project": "Include projects",
        "education": "Add education section",
        "skills": "Include skills section",
    }

    for key, message in checks.items():
        if key in text:
            score += 1
        else:
            feedback.append(message)

    # Technical keywords
    if any(word in text for word in ["python", "java", "sql", "javascript"]):
        score += 1
    else:
        feedback.append("Add technical skills")

    # Measurable achievements
    if any(char.isdigit() for char in text):
        score += 1
    else:
        feedback.append("Add measurable achievements")

    return score, feedback


# -------------------------------
# 🎯 MATCHING LOGIC
# -------------------------------

def keyword_match_score(cv_text: str, job_text: str):
    if not job_text:
        return None

    cv_words = set(re.findall(r"\w+", cv_text.lower()))
    job_words = set(re.findall(r"\w+", job_text.lower()))

    if not job_words:
        return None

    matches = cv_words.intersection(job_words)

    return int((len(matches) / len(job_words)) * 100)


# -------------------------------
# 🚀 API ROUTE
# -------------------------------

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    job_description: str = Form("")
):
    try:
        filename = file.filename.lower()

        # 🔒 Validate file type
        if not filename.endswith(ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use PDF, DOCX, or TXT."
            )

        # Read file
        file_bytes = await file.read()

        # 🔒 Validate file size
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 5MB)"
            )

        # Extract text
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(file_bytes)
        else:
            text = extract_text_from_txt(file_bytes)

        # 🔒 Validate extracted text
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract readable text from file"
            )

        # Analyse CV
        score, feedback = analyse_cv(text)

        # ATS Score
        ats_score = keyword_match_score(text, job_description)

        # Job Match Score (same logic but explicit)
        job_match_score = keyword_match_score(text, job_description)

        return {
            "score": score,
            "max_score": MAX_SCORE,
            "feedback": feedback,
            "ats_score": ats_score,
            "job_match_score": job_match_score
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )