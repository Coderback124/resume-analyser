# Resume Analyser

## Features
- Upload PDF, DOCX, or TXT CVs
- Automatic CV analysis
- Score + feedback system

## Tech Stack
- FastAPI (Backend)
- React + Vite (Frontend)

## Setup

### Backend
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev