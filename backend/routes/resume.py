import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pypdf.errors import PdfReadError

from backend.services.ai_json import AIResponseError
from backend.services.resume_ai import analyze_resume, improve_resume
from backend.services.resume_parser import extract_resume_text
from backend.services.resume_pdf import create_improved_resume_pdf


router = APIRouter(prefix="/resume", tags=["Resume"])


async def get_resume_text(file: UploadFile) -> str:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF files are allowed.")

    temp_file_path = ""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded PDF is empty.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        resume_text = extract_resume_text(temp_file_path).strip()
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No readable text could be extracted from this PDF.",
            )
        return resume_text
    except PdfReadError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="The uploaded file is not a readable PDF.") from error
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    resume_text = await get_resume_text(file)
    return {"message": "Resume uploaded successfully", "filename": file.filename, "text": resume_text}


@router.post("/analyze")
async def analyze_uploaded_resume(file: UploadFile = File(...)):
    resume_text = await get_resume_text(file)
    try:
        analysis = analyze_resume(resume_text)
    except AIResponseError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error

    return {"message": "Resume analyzed successfully", "filename": file.filename, "analysis": analysis}


@router.post("/improve")
async def improve_uploaded_resume(file: UploadFile = File(...)):
    resume_text = await get_resume_text(file)
    try:
        improved_resume = improve_resume(resume_text)
    except AIResponseError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error

    return {
        "message": "Resume improvement generated successfully",
        "filename": file.filename,
        "improved_resume": improved_resume,
        "download_url": f"/downloads/{create_improved_resume_pdf(improved_resume)}",
    }
