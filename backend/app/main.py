from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router

app = FastAPI(
    title="Resume Analyser API",
    version="1.0.0"
)

# CORS (ALLOW FRONTEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(upload_router, prefix="")

# ROOT ENDPOINT
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Resume Analyser API is running"
    }