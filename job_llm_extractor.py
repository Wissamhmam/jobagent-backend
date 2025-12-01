from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

client.models.list()

def extract_job_data(job_description: str):
    prompt = f"""
You are an AI system that extracts structured information from job descriptions.

Return a JSON with EXACTLY these fields:

{{
  "required_skills": [],
  "responsibilities": [],
  "years_experience": "",
  "seniority_level": "",
  "tech_stack": [],
  "keywords": [],
  "job_language": "",
  "summary": ""
}}

Job Description:
{job_description}
    """

    response = client.responses.create(
        model="openai/gpt-oss-120b",
        input=prompt
    )

    # Get the text output
    cleaned = response.output[0].content[0].text.strip()

    # Ensure it's JSON-like
    import re
    json_start = cleaned.find("{")
    json_end = cleaned.rfind("}")
    if json_start == -1 or json_end == -1:
        # Fallback: return empty structure
        return {
            "required_skills": [],
            "responsibilities": [],
            "years_experience": "",
            "seniority_level": "",
            "tech_stack": [],
            "keywords": [],
            "job_language": "",
            "summary": ""
        }

    json_text = cleaned[json_start:json_end+1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        # fallback if minor formatting issues
        import ast
        return ast.literal_eval(json_text)
