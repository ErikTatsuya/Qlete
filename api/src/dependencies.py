from hmac import compare_digest

from fastapi import HTTPException, Request, status

from src.core.admin_tokens import decode_admin_token
from src.core.config import ADMIN_PASSWORD, ADMIN_USER


async def require_admin(request: Request) -> str:
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Credenciais de administrador não configuradas.",
        )

    token = request.cookies.get("admin_token")
    username = decode_admin_token(token) if token else None
    if username and compare_digest(username, ADMIN_USER):
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sem sessão ativa.",
    )