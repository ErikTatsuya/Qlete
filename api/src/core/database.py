from collections.abc import AsyncIterator

from sqlalchemy import Connection, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import DATABASE_URL


engine = create_async_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = (
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    if engine
    else None
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncIterator[AsyncSession]:
    session_factory = SessionLocal
    if session_factory is None:
        raise RuntimeError("Configure DATABASE_URL com a URL do PostgreSQL remoto.")
    async with session_factory() as db:
        yield db


def _initialize_schema(connection: Connection) -> None:
    import src.models

    Base.metadata.create_all(bind=connection)
    question_columns = {column["name"] for column in inspect(connection).get_columns("questions")}
    if "correct_alternative" not in question_columns:
        connection.execute(
            text(
                "ALTER TABLE questions ADD COLUMN correct_alternative "
                "INTEGER NOT NULL DEFAULT 1 CHECK (correct_alternative BETWEEN 1 AND 4)"
            )
        )


async def init_db() -> None:
    if engine is None:
        raise RuntimeError("Configure DATABASE_URL com a URL do PostgreSQL remoto.")
    async with engine.begin() as connection:
        await connection.run_sync(_initialize_schema)


async def close_db() -> None:
    if engine is not None:
        await engine.dispose()