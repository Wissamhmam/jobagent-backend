import os
from fastapi import Header, HTTPException
from supabase_conn import supabase


def _get_user_from_token(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Invalid access token")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


async def require_authenticated_user(authorization: str | None = Header(default=None)):
    return _get_user_from_token(authorization)


async def require_admin_user(authorization: str | None = Header(default=None)):
    user = _get_user_from_token(authorization)
    admin_ids = {
        value.strip()
        for value in os.getenv("JOB_ADMIN_USER_IDS", "").split(",")
        if value.strip()
    }
    if not admin_ids:
        raise HTTPException(status_code=503, detail="Admin access is not configured. Set JOB_ADMIN_USER_IDS.")
    if user.id not in admin_ids:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
