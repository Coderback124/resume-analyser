from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.improve import router as improve_router
from app.routes.resume_pdf import router as resume_pdf_router
from app.routes.upload import router as upload_router


app = FastAPI(
    title="Resume Analyser API",
    version="1.1.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(upload_router)
app.include_router(improve_router)
app.include_router(resume_pdf_router)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Resume Analyser API is running",
        "version": "1.1.0",
    }