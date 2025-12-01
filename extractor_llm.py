from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def extract_resume_fields(text: str):
    """
    Extract structured information from a resume using Groq LLM.
    Supports English & French resumes.
    """

    prompt = f"""
Extract structured information from the following resume (English or French).

Return JSON with EXACTLY these fields:

{{
  "name": "",
  "job_title": "",
  "email": "",
  "phone": "",
  "address": "",
  "links": [],
  "summary": [],
  "skills": [],
  "experience": [
      {{
        "company": "",
        "role": "",
        "start_date": "",
        "end_date": "",
        "description": ""
      }}
  ],
  "projects": [],
  "education": [],
  "certifications": [],
  "languages": [],
  "keywords": []
}}

=========================
STRICT EXTRACTION RULES
=========================

LANGUAGE SUPPORT:
- Resume text may be in English or French.
- Detect French terms: "expérience", "compétences", "projets", "éducation", etc.

GENERAL RULES:
1. Extract EVERY PIECE OF INFORMATION present in the text.
2. Never leave a field empty if the information exists.
3. If it does NOT exist → return empty string or empty list.

FIELD RULES:

NAME:
- Extract the full name (any order).

JOB TITLE:
- Extract the candidate’s main professional title.

EMAIL & PHONE:
- Extract all emails/phones (return main ones).

ADDRESS:
- Extract city, region, country, postal code, or any location.

LINKS:
- Extract LinkedIn, GitHub, portfolio, personal website, Behance, etc.

SUMMARY:
- Short intro sentences or bullet points.

SKILLS:
- Technical + soft skills.
- Return list of strings.

EXPERIENCE:
- For EACH job extract:
  - company
  - role
  - start_date
  - end_date
  - description (preserve bullet points)

PROJECTS:
- Personal, academic, professional projects.

EDUCATION:
- Degrees, schools, programs, dates.

CERTIFICATIONS:
- All certificates ("AWS Certified", "Coursera", etc.)

LANGUAGES:
- Spoken languages + proficiency (English/French).

KEYWORDS (VERY IMPORTANT):
- Extract technologies, tools, frameworks, domains.
- MUST NOT be empty.

Resume text:
{text}
"""

    # Call Groq API
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # Raw LLM output
    raw_output = completion.choices[0].message.content

    # Ensure valid JSON
    try:
        return json.loads(raw_output)

    except json.JSONDecodeError:
        # Try extracting JSON from text
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    # Return empty object if all parsing fails
    return {}
