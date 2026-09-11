import logging
import httpx
from typing import Optional
from fastapi import Header, HTTPException, Depends
from app.config import settings

logger = logging.getLogger("auth_service")

ALLOWED_ROLES = {"user", "driver", "officer"}
SELF_SERVICE_ROLES = {"user", "driver"}  # officer accounts are never created via public signup


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verifies the bearer token against Supabase and returns {id, email, role}.
    `role` is read from app_metadata (server-controlled), never user_metadata
    (client-editable) — that distinction is what makes this trustworthy for
    authorization decisions.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sign-in required.")

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(status_code=503, detail="Auth service not configured (missing Supabase settings).")

    token = authorization.split(" ")[1]
    url = f"{settings.SUPABASE_URL}/auth/v1/user"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}", "apikey": settings.SUPABASE_ANON_KEY},
            )
            if res.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")
            user_data = res.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supabase auth check failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication service unavailable.")

    role = (user_data.get("app_metadata") or {}).get("role", "user")
    if role not in ALLOWED_ROLES:
        role = "user"

    return {
        "id": user_data.get("id"),
        "email": user_data.get("email"),
        "role": role,
    }


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Like get_current_user, but returns None instead of raising when there's no
    (or an invalid) bearer token — for endpoints usable both signed-in and as
    a guest, where a real identity is preferred but not required.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None


def require_role(*roles: str):
    """Dependency factory: require_role('officer') or require_role('driver', 'officer')."""
    async def _dependency(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"This action requires one of these roles: {', '.join(roles)}.",
            )
        return user
    return _dependency


async def register_user(email: str, password: str, role: str) -> dict:
    """
    Creates a Supabase user via the Admin API using the service_role key, and
    sets `role` in app_metadata server-side. Officer accounts are deliberately
    excluded from self-service — see register_officer().
    """
    if role not in SELF_SERVICE_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role for self-service signup.")
    return await _admin_create_user(email, password, role)


async def register_officer(email: str, password: str, invite_code: str) -> dict:
    """Officer signup gated behind a shared invite code (see OFFICER_INVITE_CODE in .env)."""
    if not settings.OFFICER_INVITE_CODE or invite_code != settings.OFFICER_INVITE_CODE:
        raise HTTPException(status_code=403, detail="Invalid officer invite code.")
    return await _admin_create_user(email, password, "officer")


async def _admin_create_user(email: str, password: str, role: str) -> dict:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=503, detail="Auth service not configured (missing service role key).")

    url = f"{settings.SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,  # auto-confirm: no SMTP setup in this build
        "app_metadata": {"role": role},
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code not in (200, 201):
                detail = res.json().get("msg") or res.json().get("message") or "Registration failed."
                raise HTTPException(status_code=400, detail=detail)
            user_data = res.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supabase admin create-user failed: {e}")
        raise HTTPException(status_code=503, detail="Auth service unavailable.")

    return {"id": user_data.get("id"), "email": user_data.get("email"), "role": role}
