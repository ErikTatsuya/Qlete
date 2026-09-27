from hmac import compare_digest

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.core.config import ADMIN_PASSWORD, ADMIN_USER


security = HTTPBasic()


async def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Credenciais de administrador não configuradas.",
        )

    username_ok = compare_digest(credentials.username, ADMIN_USER)
    password_ok = compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username