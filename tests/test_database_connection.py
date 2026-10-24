"""
Mock-based unit tests for TrueMark PostgreSQL database connection module.

These tests verify:
- Missing configuration handling
- Session cleanup and transaction rollback on failure
- Successful health check (SELECT 1)
- Connection failure handling and credential masking
- Engine caching and lazy initialization (no connection on import)

None of these tests require a running PostgreSQL server.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from database.connection import (
    DatabaseConfigError,
    DatabaseConnectionError,
    check_database_connection,
    get_database_url,
    get_db,
    get_engine,
    get_session_factory,
    reset_connection,
    sanitize_credentials,
    sanitize_url,
)


class TestDatabaseConnection(unittest.TestCase):
    """Unit test suite for database/connection.py."""

    def setUp(self):
        # Reset cached singletons before each test
        reset_connection()

    def tearDown(self):
        # Reset cached singletons after each test
        reset_connection()

    # --------------------------------------------------------------------------
    # 1. Missing Configuration Tests
    # --------------------------------------------------------------------------

    def test_missing_database_url_raises_config_error(self):
        """get_database_url must raise DatabaseConfigError when DATABASE_URL is unset or empty."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(DatabaseConfigError) as ctx:
                get_database_url(load_env=False)
            self.assertIn("DATABASE_URL is not configured", str(ctx.exception))

    def test_empty_database_url_raises_config_error(self):
        """get_database_url must raise DatabaseConfigError when DATABASE_URL is whitespace."""
        with patch.dict(os.environ, {"DATABASE_URL": "   "}, clear=True):
            with self.assertRaises(DatabaseConfigError) as ctx:
                get_database_url(load_env=False)
            self.assertIn("DATABASE_URL is not configured", str(ctx.exception))

    def test_get_engine_fails_on_missing_configuration(self):
        """get_engine must raise DatabaseConfigError if DATABASE_URL is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("database.connection.load_dotenv"):
                with self.assertRaises(DatabaseConfigError):
                    get_engine()

    def test_health_check_handles_missing_configuration(self):
        """check_database_connection returns False (or raises when requested) if config is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("database.connection.load_dotenv"):
                # By default, health check should return False without crashing
                self.assertFalse(check_database_connection(raise_on_error=False))

                # When raise_on_error is True, it should raise DatabaseConfigError
                with self.assertRaises(DatabaseConfigError):
                    check_database_connection(raise_on_error=True)

    # --------------------------------------------------------------------------
    # 2. Scheme Normalization Tests
    # --------------------------------------------------------------------------

    def test_database_url_normalizes_to_psycopg_driver(self):
        """Ensures postgres:// and postgresql:// are normalized to postgresql+psycopg://."""
        test_cases = [
            (
                "postgres://user:pass@localhost:5432/db",
                "postgresql+psycopg://user:pass@localhost:5432/db",
            ),
            (
                "postgresql://user:pass@localhost:5432/db",
                "postgresql+psycopg://user:pass@localhost:5432/db",
            ),
            (
                "postgresql+psycopg://user:pass@localhost:5432/db",
                "postgresql+psycopg://user:pass@localhost:5432/db",
            ),
        ]
        for input_url, expected_url in test_cases:
            with patch.dict(os.environ, {"DATABASE_URL": input_url}):
                url = get_database_url(load_env=False)
                self.assertEqual(url, expected_url)

    # --------------------------------------------------------------------------
    # 3. Session Cleanup Tests
    # --------------------------------------------------------------------------

    def test_session_cleanup_on_normal_execution(self):
        """get_db must close session upon completion of generator."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        with patch("database.connection.get_session_factory", return_value=mock_factory):
            gen = get_db()
            yielded_session = next(gen)
            self.assertEqual(yielded_session, mock_session)
            mock_session.close.assert_not_called()

            # Finish iteration
            with self.assertRaises(StopIteration):
                next(gen)

            # Assert session was closed
            mock_session.close.assert_called_once()
            mock_session.rollback.assert_not_called()

    def test_session_cleanup_and_rollback_on_exception(self):
        """get_db must rollback and close session when an exception occurs."""
        mock_session = MagicMock(spec=Session)
        mock_factory = MagicMock(return_value=mock_session)

        with patch("database.connection.get_session_factory", return_value=mock_factory):
            gen = get_db()
            yielded_session = next(gen)
            self.assertEqual(yielded_session, mock_session)

            # Throw exception into generator
            test_exc = RuntimeError("Simulated transaction error")
            with self.assertRaises(RuntimeError) as ctx:
                gen.throw(test_exc)

            self.assertEqual(ctx.exception, test_exc)
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    # --------------------------------------------------------------------------
    # 4. Successful Health Check Tests
    # --------------------------------------------------------------------------

    def test_check_database_connection_success(self):
        """check_database_connection executes SELECT 1 and returns True when result is 1."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1

        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with patch("database.connection.get_engine", return_value=mock_engine):
            result = check_database_connection()

            self.assertTrue(result)
            mock_engine.connect.assert_called_once()
            mock_conn.execute.assert_called_once()
            executed_sql = str(mock_conn.execute.call_args[0][0])
            self.assertIn("SELECT 1", executed_sql)

    def test_check_database_connection_unexpected_scalar(self):
        """check_database_connection returns False if SELECT 1 returns non-1."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0

        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with patch("database.connection.get_engine", return_value=mock_engine):
            result = check_database_connection()
            self.assertFalse(result)

    # --------------------------------------------------------------------------
    # 5. Connection Failure & Credential Masking Tests
    # --------------------------------------------------------------------------

    def test_check_database_connection_failure_returns_false(self):
        """check_database_connection logs error and returns False by default on connection error."""
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = OperationalError("SELECT 1", {}, "Connection refused")

        with patch("database.connection.get_engine", return_value=mock_engine):
            result = check_database_connection(raise_on_error=False)
            self.assertFalse(result)

    def test_check_database_connection_failure_raises_sanitized_error(self):
        """check_database_connection raises DatabaseConnectionError with credentials masked."""
        secret_password = "SuperSecretPassword123!"
        sensitive_error = (
            f"Failed to connect to postgresql+psycopg://rahul:{secret_password}@localhost:5432/truemark_db: "
            "password authentication failed"
        )
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = OperationalError("SELECT 1", {}, sensitive_error)

        with patch("database.connection.get_engine", return_value=mock_engine):
            with self.assertRaises(DatabaseConnectionError) as ctx:
                check_database_connection(raise_on_error=True)

            err_msg = str(ctx.exception)
            self.assertNotIn(secret_password, err_msg)
            self.assertIn("***", err_msg)
            self.assertIn("rahul:***", err_msg)

    def test_sanitize_credentials_helper(self):
        """Verifies regex credential sanitization for URLs and DSNs."""
        raw_url = "postgresql+psycopg://app_user:MySecretP@ss!@db.internal:5432/prod_db"
        sanitized = sanitize_credentials(raw_url)
        self.assertNotIn("MySecretP@ss!", sanitized)
        self.assertEqual(
            sanitized,
            "postgresql+psycopg://app_user:***@db.internal:5432/prod_db",
        )

        raw_dsn = "host=localhost port=5432 user=rahul password=SecretKey123 dbname=test"
        sanitized_dsn = sanitize_credentials(raw_dsn)
        self.assertNotIn("SecretKey123", sanitized_dsn)
        self.assertIn("password=***", sanitized_dsn)

    # --------------------------------------------------------------------------
    # 6. Reusable Engine and No Connection on Import Tests
    # --------------------------------------------------------------------------

    def test_no_connection_opened_on_import(self):
        """Importing database.connection must not open connections or create engines."""
        import database.connection as conn_module

        # _engine should be None on initial clean state
        self.assertIsNone(conn_module._engine)
        self.assertIsNone(conn_module._session_factory)

    def test_reusable_engine_and_sessionmaker(self):
        """Calling get_engine and get_session_factory multiple times reuses singletons."""
        dummy_url = "postgresql+psycopg://user:pass@localhost:5432/db"
        with patch.dict(os.environ, {"DATABASE_URL": dummy_url}):
            with patch("database.connection.create_engine") as mock_create_engine:
                mock_engine_instance = MagicMock()
                mock_create_engine.return_value = mock_engine_instance

                # First call
                e1 = get_engine()
                # Second call
                e2 = get_engine()

                self.assertIs(e1, e2)
                mock_create_engine.assert_called_once()

                # Session factory
                f1 = get_session_factory()
                f2 = get_session_factory()
                self.assertIs(f1, f2)


if __name__ == "__main__":
    unittest.main()
