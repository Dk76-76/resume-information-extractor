"""FastAPI application for Resume Information Extraction System."""

import os
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.extractor import ResumeExtractor
from app.parser import (
    CorruptedFileError,
    DocumentParserError,
    EmptyDocumentError,
    NoTextFoundError,
    UnsupportedFileTypeError,
    extract_document_layout,
    extract_text_from_file,
)
from app.schemas import ExtractionResponse, ResumeData

app = FastAPI(
    title="Resume Information Extraction System",
    description="Local, rule-based Resume Information Extraction API without external LLMs or GenAI.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "service": "Resume Information Extraction System",
        "version": "1.0.0",
        "llm_free": True
    }


@app.post("/api/extract", response_model=ExtractionResponse)
async def extract_resume(file: UploadFile = File(...)):
    """Uploads a PDF or DOCX resume and extracts structured data locally."""
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided."
        )

    filename = file.filename
    try:
        file_bytes = await file.read()
        raw_text, spans = extract_document_layout(file_bytes, filename)
        
        extractor = ResumeExtractor(raw_text, blocks_metadata=spans)
        resume_data: ResumeData = extractor.extract_all()

        return ExtractionResponse(
            success=True,
            filename=filename,
            message="Resume information extracted successfully.",
            data=resume_data
        )

    except EmptyDocumentError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "filename": filename,
                "message": f"Empty file error: {str(exc)}",
                "data": None
            }
        )
    except UnsupportedFileTypeError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "filename": filename,
                "message": f"Unsupported format: {str(exc)}",
                "data": None
            }
        )
    except (CorruptedFileError, NoTextFoundError) as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "filename": filename,
                "message": f"Parsing failure: {str(exc)}",
                "data": None
            }
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "filename": filename,
                "message": f"An unexpected error occurred during extraction: {str(exc)}",
                "data": None
            }
        )


# Serve frontend static assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Serve sample files for the UI quick demo
SAMPLES_DIR = BASE_DIR / "samples"
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")


@app.get("/")
async def serve_index():
    """Serves the frontend single-page interface."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend UI index.html not found. Access /docs for API documentation."}

