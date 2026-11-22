from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from pathlib import Path

from extract_resume import process_resume
from supabase_conn import supabase
from extractor_llm import extract_resume_fields
from routes.jobs import router as jobs_router
from routes.job_process import router as job_process_router
from auth import require_authenticated_user

app = FastAPI()
app.include_router(jobs_router)
app.include_router(job_process_router)

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

MAX_RESUME_SIZE = 10 * 1024 * 1024


@app.post("/upload_resume")
async def upload_resume(file: UploadFile, current_user=Depends(require_authenticated_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF resumes are accepted")
    content = await file.read(MAX_RESUME_SIZE + 1)
    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=413, detail="Resume exceeds the 10 MB limit")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="Uploaded file is not a valid PDF")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        parsed = process_resume(temp_path)
        full_text = parsed.get("text", "")
        lang = parsed.get("lang", "en")
        if not full_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from this PDF")

        extracted = extract_resume_fields(full_text)
        user_id = str(current_user.id)
        full_insert = supabase.table("profiles_full").upsert({
            "user_id": user_id, "name": extracted.get("name", ""),
            "job_title": extracted.get("job_title", ""), "address": extracted.get("address", ""),
            "links": extracted.get("links", []), "email": extracted.get("email", ""),
            "phone": extracted.get("phone", ""), "resume_text": full_text, "cv_lang": lang,
        }, on_conflict="user_id").execute()
        safe_insert = supabase.table("profiles_safe").upsert({
            "user_id": user_id, "job_title": extracted.get("job_title", ""),
            "summary": extracted.get("summary", []), "skills": extracted.get("skills", []),
            "experience": extracted.get("experience", []), "projects": extracted.get("projects", []),
            "education": extracted.get("education", []), "keywords": extracted.get("keywords", []),
            "certifications": extracted.get("certifications", []), "languages": extracted.get("languages", []),
            "cv_lang": lang,
        }, on_conflict="user_id").execute()
        return {"status": "complete", "user_id": user_id, "language": lang,
                "full_profile": full_insert.data, "safe_profile": safe_insert.data}
    finally:
        await file.close()
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()
