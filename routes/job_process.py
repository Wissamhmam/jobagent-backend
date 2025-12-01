from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_conn import supabase
from job_llm_extractor import extract_job_data
from uuid import UUID

router = APIRouter()

class JobToProcess(BaseModel):
    job_id: str

@router.post("/process_job_posting")
def process_job_posting(data: JobToProcess):

    # 1. Validate UUID
    try:
        job_uuid = UUID(data.job_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid job_id format. Must be UUID.")

    # 2. Fetch job safely (NO .single())
    result = supabase.table("jobs").select("*").eq("id", str(job_uuid)).execute()

    # result.data is a LIST
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Job not found in database")

    # Extract actual row
    job = result.data[0]

    description = job.get("job_description")
    if not description:
        raise HTTPException(status_code=400, detail="Job has no job_description field")

    # 3. Extract structured info using LLM
    extracted = extract_job_data(description)

    # 4. Update DB
    supabase.table("jobs").update({
        "job_language": extracted.get("job_language"),
        "keywords": extracted.get("keywords"),
        "responsibilities": extracted.get("responsibilities"),
        "required_skills": extracted.get("required_skills"),
        "seniority_level": extracted.get("seniority_level"),
    }).eq("id", str(job_uuid)).execute()

    return {
        "status": "processed",
        "job_id": data.job_id,
        "extracted": extracted
    }
