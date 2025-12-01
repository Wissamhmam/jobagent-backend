from fastapi import FastAPI, UploadFile, Query
import os
import uuid
from extract_resume import process_resume
from supabase_conn import supabase
from fastapi.middleware.cors import CORSMiddleware
from extractor_llm import extract_resume_fields
import json
from routes.jobs import router as jobs_router
from routes.job_process import router as job_process_router

app = FastAPI()

app.include_router(jobs_router)
app.include_router(job_process_router)

origins = [
    "http://localhost:3000",   # local frontend
    "https://jobagent-13245ux5z-hwissm-2040s-projects.vercel.app",  # Vercel frontend
    "https://jobagent-6j1ypkq4t-hwissm-2040s-projects.vercel.app",
    "https://jobagent-gu4sw86o4-hwissm-2040s-projects.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_resume")
async def upload_resume(file: UploadFile, user_id: str = Query(None)):
    os.makedirs("storage", exist_ok=True)

    file_path = f"storage/{file.filename}"

    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text & language
    parsed = process_resume(file_path)
    full_text = parsed.get("text", "")
    lang = parsed.get("lang", "en")

    # Generate user_id if missing
    if not user_id:
        user_id = str(uuid.uuid4())

    # Run the AI extractor (automatically)
    extracted = extract_resume_fields(full_text)

    # -------------------------
    # INSERT INTO profiles_full
    # -------------------------
    full_insert = supabase.table("profiles_full").upsert({
    "user_id": user_id,
    "name": extracted.get("name", ""),
    "job_title": extracted.get("job_title", ""),
    "address": extracted.get("address", ""),
    "links": extracted.get("links", []),
    "email": extracted.get("email", ""),
    "phone": extracted.get("phone", ""),
    "resume_text": full_text,
    "cv_lang": lang
    }, on_conflict="user_id").execute()


    # -------------------------
    # INSERT INTO profiles_safe
    # -------------------------
    safe_insert = supabase.table("profiles_safe").upsert({
    "user_id": user_id,
    "job_title": extracted.get("job_title", ""),
    "summary": extracted.get("summary", []),
    "skills": extracted.get("skills", []),
    "experience": extracted.get("experience", []),
    "projects": extracted.get("projects", []),
    "education": extracted.get("education", []),
    "keywords": extracted.get("keywords", []),
    "certifications": extracted.get("certifications", []),
    "languages": extracted.get("languages", []),
    "cv_lang": lang
    }, on_conflict="user_id").execute()


    return {
        "status": "complete",
        "user_id": user_id,
        "language": lang,
        "full_profile": full_insert.data,
        "safe_profile": safe_insert.data
    }