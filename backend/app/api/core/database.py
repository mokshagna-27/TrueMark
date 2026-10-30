
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load the .env file from the TrueMark project root.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # No DATABASE_URL configured (e.g. first-time local setup with no Postgres
    # instance available yet). Fall back to a local SQLite file so the app is
    # runnable out of the box. Set DATABASE_URL in .env to use Postgres instead.
    # Serverless hosts (Vercel/Lambda) have a read-only project directory;
    # only /tmp is writable there (and not persistent - use Postgres in prod).
    _db_dir = Path("/tmp") if (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")) else PROJECT_ROOT
    DATABASE_URL = f"sqlite:///{_db_dir / 'truemark_local.db'}"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()

