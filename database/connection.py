"""
PostgreSQL database connection management for TrueMark using SQLAlchemy 2.x and psycopg.

Provides:
- Reusable, lazily-initialized SQLAlchemy engine and sessionmaker.
- get_db() generator for session lifecycle management.
- check_database_connection() health-check verifying DB connectivity via SELECT 1.
- Safe credential handling and masking in logs and error messages.
"""

from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING, Any, Generator, Optional

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# Cached singletons
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


class DatabaseConfigError(ValueError):
    """Raised when database configuration is missing or invalid."""
    pass


class DatabaseConnectionError(RuntimeError):
    """Raised when establishing a database connection fails."""
    pass


def sanitize_credentials(message: str) -> str:
    """
    Mask passwords and sensitive credentials in URLs, DSNs, and error messages.
    Handles special characters (including '@' and percent-encoded values) in passwords.
    """
    if not message:
        return ""
    # Mask passwords in standard URI schemes: scheme://user:password@host[:port][/...]
    sanitized = re.sub(
        r"(://[^/:@\s]+:)(.+?)(@[^/:@\s]+(?::\d+)?(?:/|\s|$|[?;]|\.))",
        r"\1***\3",
        message,
    )
    # Mask password parameters in DSN or query formats: password=xyz or pwd=xyz
    sanitized = re.sub(
        r"(password|pwd)=([^\s;&]+)",
        r"\1=***",
        sanitized,
        flags=re.IGNORECASE,
    )
    return sanitized


def sanitize_url(url: str) -> str:
    """Mask credentials in a database URL string."""
    try:
        parsed = make_url(url)
        return parsed.render_as_string(hide_password=True)
    except Exception:
        return sanitize_credentials(url)


def get_database_url(load_env: bool = True) -> str:
    """
    Retrieve and validate the DATABASE_URL from environment variables.

    Args:
        load_env: Whether to load variables from local .env if present.
                 Defaults to True, without overwriting existing environment variables.

    Returns:
        str: Validated database connection URL with normalized psycopg driver scheme.

    Raises:
        DatabaseConfigError: If DATABASE_URL is not set or empty.
    """
    if load_env:
        load_dotenv(find_dotenv(), override=False)

    raw_url = os.getenv("DATABASE_URL")
    if not raw_url or not raw_url.strip():
        raise DatabaseConfigError(
            "DATABASE_URL is not configured. Please set the DATABASE_URL environment variable."
        )

    url = raw_url.strip()

    # Normalize PostgreSQL schemes to explicitly use the modern psycopg (v3) driver
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]

    return url


def get_engine() -> Engine:
    """
    Retrieve or create the reusable SQLAlchemy Engine singleton.

    Connections are pooled and managed lazily; no socket connection is established
    until a connection or session is actually checked out.
    """
    global _engine
    if _engine is None:
        url = get_database_url()
        masked = sanitize_url(url)
        logger.info("Initializing SQLAlchemy engine for %s", masked)
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            future=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """
    Retrieve or create the reusable SQLAlchemy sessionmaker singleton.
    """
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session and guarantee cleanup upon exit.

    Rolls back any uncommitted transaction if an exception occurs during use,
    and always closes the session in the finally block.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connection(raise_on_error: bool = False) -> bool:
    """
    Health-check function verifying database connectivity by executing SELECT 1.

    Args:
        raise_on_error: If True, raises DatabaseConnectionError on failure.
                       If False (default), logs sanitized error and returns False.

    Returns:
        bool: True if connection is healthy and SELECT 1 returns 1, False otherwise.
    """
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            scalar = result.scalar()
            return scalar == 1
    except DatabaseConfigError as exc:
        logger.error("Database health check failed due to missing configuration: %s", exc)
        if raise_on_error:
            raise
        return False
    except Exception as exc:
        sanitized_msg = sanitize_credentials(str(exc))
        logger.error("Database health check failed: %s", sanitized_msg)
        if raise_on_error:
            raise DatabaseConnectionError(
                f"Database health check failed: {sanitized_msg}"
            ) from None
        return False


def reset_connection() -> None:
    """
    Dispose and clear cached engine and session factory singletons.
    Primarily used for testing or re-initialization.
    """
    global _engine, _session_factory
    if _engine is not None:
        try:
            _engine.dispose()
        except Exception:
            pass
        _engine = None
    _session_factory = None


# Module-level attribute access for lazy engine and SessionLocal
def __getattr__(name: str) -> Any:
    if name == "engine":
        return get_engine()
    if name == "SessionLocal":
        return get_session_factory()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


if TYPE_CHECKING:
    engine: Engine
    SessionLocal: sessionmaker[Session]


__all__ = [
    "DatabaseConfigError",
    "DatabaseConnectionError",
    "sanitize_credentials",
    "sanitize_url",
    "get_database_url",
    "get_engine",
    "get_session_factory",
    "get_db",
    "check_database_connection",
    "reset_connection",
    "engine",
    "SessionLocal",
]
