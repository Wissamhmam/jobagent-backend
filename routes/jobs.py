from fastapi import APIRouter, Depends
from pydantic import BaseModel
from supabase_conn import supabase
from auth import require_admin_user

router = APIRouter()


class JobPosting(BaseModel):
    title: str
    company: str | None = None
    location: str | None = None
    job_link: str | None = None
    job_description: str
    hr_name: str | None = None
    hr_email: str | None = None
    hr_linkedin: str | None = None
    job_language: str | None = None


@router.post("/add_job_posting")
def add_job_posting(job: JobPosting, current_user=Depends(require_admin_user)):
    response = supabase.table("jobs").insert(job.model_dump()).execute()
    return {"status": "success", "inserted": response.data}
