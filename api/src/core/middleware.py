from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import FRONTEND_ORIGINS


LOCAL_ORIGIN_REGEX = (
    r"^https?://(localhost|127\.0\.0\.1|\[::1\]|10(?:\.\d{1,3}){3}|"
    r"192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?::\d+)?$"
)


def configure_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_origin_regex=LOCAL_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Cookie"],
    )