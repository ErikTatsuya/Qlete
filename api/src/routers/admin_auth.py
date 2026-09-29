from fastapi import APIRouter, HTTPException, Request, Response, status
from hmac import compare_digest

from src.core.admin_tokens import create_admin_token, decode_admin_token
from src.core.config import ADMIN_COOKIE_SECURE, ADMIN_PASSWORD, ADMIN_SESSION_TTL_SECONDS, ADMIN_USER
from src.schemas import AdminLogin, AdminSession

router = APIRouter(prefix="/admin", tags=["admin-auth"])


@router.post("/login")
async def login_admin(payload: AdminLogin, request: Request, response: Response):
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

    cookie_secure = ADMIN_COOKIE_SECURE or request.url.scheme == "https"
    response.set_cookie(
        key="admin_token",
        value=create_admin_token(payload.username),
        httponly=True,
        samesite="none" if cookie_secure else "lax",
        secure=cookie_secure,
        max_age=ADMIN_SESSION_TTL_SECONDS,
        path="/",
    )
    return AdminSession(username=payload.username)


@router.post("/logout")
async def logout_admin(response: Response):
    response.delete_cookie(key="admin_token", path="/")
    return {"status": "logged_out"}


@router.get("/me", response_model=AdminSession)
async def get_admin_session(request: Request):
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Credenciais de administrador não configuradas.",
        )

    token = request.cookies.get("admin_token")
    username = decode_admin_token(token) if token else None
    if not username or not compare_digest(username, ADMIN_USER):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sem sessão ativa.")
    return AdminSession(username=username)
