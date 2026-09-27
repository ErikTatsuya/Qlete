import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url


API_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(API_ROOT / ".env")

def async_database_url(database_url: str | None) -> str | None:
	if not database_url:
		return None

	if database_url.startswith("postgres://"):
		database_url = "postgresql://" + database_url.removeprefix("postgres://")

	parsed_url = make_url(database_url)
	if parsed_url.get_backend_name() != "postgresql":
		raise ValueError("DATABASE_URL deve apontar para um banco PostgreSQL remoto.")
	if parsed_url.drivername in ("postgresql", "postgresql+asyncpg"):
		parsed_url = parsed_url.set(drivername="postgresql+psycopg")
	elif parsed_url.drivername != "postgresql+psycopg":
		raise ValueError("Use o driver assíncrono postgresql+psycopg em DATABASE_URL.")
	return parsed_url.render_as_string(hide_password=False)


DATABASE_URL = async_database_url(os.getenv("DATABASE_URL"))
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
FRONTEND_ORIGINS = [
	origin.strip().rstrip("/")
	for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
	if origin.strip()
]