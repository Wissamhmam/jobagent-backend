from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase_conn import supabase
from job_llm_extractor import extract_job_data
from auth import require_admin_user
from uuid import UUID

router = APIRouter()


class JobToProcess(BaseModel):
    job_id: str


@router.post("/process_job_posting")
def process_job_posting(data: JobToProcess, current_user=Depends(require_admin_user)):
    try:
        job_uuid = UUID(data.job_id)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid job_id format. Must be UUID.")

    result = supabase.table("jobs").select("*").eq("id", str(job_uuid)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found in database")
    description = result.data[0].get("job_description")
    if not description:
        raise HTTPException(status_code=400, detail="Job has no job_description field")

    extracted = extract_job_data(description)
    supabase.table("jobs").update({
        "job_language": extracted.get("job_language"),
        "keywords": extracted.get("keywords"),
        "responsibilities": extracted.get("responsibilities"),
        "required_skills": extracted.get("required_skills"),
        "seniority_level": extracted.get("seniority_level"),
    }).eq("id", str(job_uuid)).execute()
    return {"status": "processed", "job_id": str(job_uuid), "extracted": extracted}
