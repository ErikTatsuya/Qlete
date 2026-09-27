from hmac import compare_digest

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.core.config import ADMIN_PASSWORD, ADMIN_USER


security = HTTPBasic(auto_error=False)


async def require_admin(
    request: Request,
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> str:
    cookie_username = request.cookies.get("admin_user")
    if cookie_username and compare_digest(cookie_username, ADMIN_USER or ""):
        return cookie_username

    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Credenciais de administrador não configuradas.",
        )

    if credentials is not None:
        username_ok = compare_digest(credentials.username, ADMIN_USER)
        password_ok = compare_digest(credentials.password, ADMIN_PASSWORD)
        if username_ok and password_ok:
            return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha incorretos.",
        headers={"WWW-Authenticate": "Basic"},
    )