import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.core.database import close_db, init_db
from src.core.middleware import configure_middleware
from src.routers.health import router as health_router
from src.routers.quizzes import router as quizzes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()


app = FastAPI(title="Qlete API", lifespan=lifespan)
configure_middleware(app)
app.include_router(health_router)
app.include_router(quizzes_router)


@app.get("/", include_in_schema=False)
async def api_root():
    return {
        "name": "Qlete API",
        "docs": "/docs",
        "health": "/health",
        "routes": {
            "list_quizzes": "GET /api/quizzes",
            "create_quiz": "POST /api/quizzes",
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        loop="src.core.event_loop:create_event_loop",
    )
