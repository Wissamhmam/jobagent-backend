from fastapi import APIRouter
from pydantic import BaseModel
from supabase_conn import supabase

router = APIRouter()

class JobPosting(BaseModel):
    title: str
    company: str = None
    location: str = None
    job_link: str = None
    job_description: str
    hr_name: str = None
    hr_email: str = None
    hr_linkedin: str = None
    job_language: str = None

@router.post("/add_job_posting")
def add_job_posting(job: JobPosting):

    data = job.dict()

    response = supabase.table("jobs").insert(data).execute()

    return {
        "status": "success",
        "inserted": response.data
    }
