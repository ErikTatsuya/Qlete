from datetime import datetime, timedelta, timezone

import jwt

from src.core.config import ADMIN_SESSION_SECRET, ADMIN_SESSION_TTL_SECONDS


ALGORITHM = "HS256"


def create_admin_token(username: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ADMIN_SESSION_TTL_SECONDS)
    return jwt.encode(
        {"sub": username, "exp": expires_at},
        ADMIN_SESSION_SECRET,
        algorithm=ALGORITHM,
    )


def decode_admin_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, ADMIN_SESSION_SECRET, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None

    username = payload.get("sub")
    return username if isinstance(username, str) and username else None