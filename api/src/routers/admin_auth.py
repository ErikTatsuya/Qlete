from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, Response, status
from hmac import compare_digest

from src.core.config import ADMIN_SESSION_TTL_SECONDS, ADMIN_PASSWORD, ADMIN_USER
from src.schemas import AdminLogin, AdminSession

router = APIRouter(prefix="/admin", tags=["admin-auth"])


@router.post("/login")
async def login_admin(payload: AdminLogin, response: Response):
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Credenciais de administrador não configuradas.",
        )

    username_ok = compare_digest(payload.username, ADMIN_USER)
    password_ok = compare_digest(payload.password, ADMIN_PASSWORD)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos.",
        )

    response.set_cookie(
        key="admin_user",
        value=payload.username,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=ADMIN_SESSION_TTL_SECONDS,
        path="/",
    )
    return AdminSession(username=payload.username)


@router.post("/logout")
async def logout_admin(response: Response):
    response.delete_cookie(key="admin_user", path="/")
    return {"status": "logged_out"}


@router.get("/me", response_model=AdminSession)
async def get_admin_session(request: Request):
    username = request.cookies.get("admin_user")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sem sessão ativa.")
    return AdminSession(username=username)
