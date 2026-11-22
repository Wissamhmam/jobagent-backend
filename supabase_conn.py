import os

from dotenv import load_dotenv
from supabase import create_client

# Load a local .env file when present; production should inject environment variables.
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be configured in the environment."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
