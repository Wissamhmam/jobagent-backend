# JobAgent Backend

FastAPI backend for a job-assistance application. The current codebase exposes resume ingestion and job-posting workflows, using PDF text extraction, language detection, LLM-based structured extraction, and Supabase persistence.

## Current capabilities

- Accepts a PDF resume upload through `POST /upload_resume`.
- Extracts text from PDF pages with `pdfplumber` and detects the language with `langdetect`.
- Uses Groq-powered extraction to structure resume details such as contact information, skills, experience, education, projects, certifications, and languages.
- Stores full and structured/safe profile records in Supabase tables named `profiles_full` and `profiles_safe`.
- Accepts job postings through `POST /add_job_posting`.
- Processes a stored job description through `POST /process_job_posting`, extracting skills, responsibilities, seniority, keywords, and language before updating the job record.

## Project structure

```text
.
├── main.py
├── extract_resume.py
├── extractor_llm.py
├── job_llm_extractor.py
├── supabase_conn.py
├── routes/
│   ├── jobs.py
│   └── job_process.py
├── requirements.txt
└── render.yaml
```

## Requirements

- Python 3.11 (as configured in `render.yaml`)
- Supabase project with the expected tables
- Groq API key for resume extraction
- OpenRouter API key for job-description extraction

## Local setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy the example environment file and fill in your own project values:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`. The application loads local values with `python-dotenv`; production deployments should define the same variables in the hosting provider's environment configuration.

Required variables:

- `SUPABASE_URL` and `SUPABASE_KEY` — Supabase project URL and API key
- `GROQ_API_KEY` — resume extraction
- `OPENAI_API_KEY` — OpenRouter API key used by the OpenAI-compatible client

Never commit a real `.env` file. Use only the least-privileged Supabase key appropriate for the backend and database policies.

Start the API:

```bash
uvicorn main:app --reload
```

FastAPI's interactive API documentation is available at `/docs` while the server is running.

## API routes

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/upload_resume` | Upload and process a PDF resume; optional `user_id` query parameter |
| `POST` | `/add_job_posting` | Insert a job posting |
| `POST` | `/process_job_posting` | Extract structured data from a stored job using its UUID |

## Deployment

The repository includes a Render Blueprint in `render.yaml`. It installs `requirements.txt` and starts Uvicorn on port 10000.

## Known limitations to address

- The current CORS middleware allows all origins while also enabling credentials; restrict this to explicit trusted frontend origins before production use.
- Resume files are saved using the uploaded filename under `storage/`; add safe filename handling, file type/size validation, and cleanup/retention controls before exposing uploads publicly.
- The repository contains an empty `process_resume.py`; the active PDF extraction implementation is in `extract_resume.py`.
- No automated test suite is currently documented.

This README describes the repository's checked-in implementation; it does not imply that external Supabase tables, provider accounts, or deployment services are configured.
