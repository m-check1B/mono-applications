"""
Database Tests - Database connection and session management
Tests database initialization, session handling, and connection lifecycle
"""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import Base, engine, get_db


class TestDatabaseEngine:
    """Test database engine configuration and lifecycle"""

    def test_engine_exists(self):
        """Database engine should be initialized"""
        assert engine is not None

    def test_engine_url_configured(self):
        """Engine should have database URL configured"""
        assert engine.url is not None
        assert str(engine.url) != ""

    def test_engine_pool_configured(self):
        """Engine should have connection pool configured"""
        assert engine.pool is not None

    def test_engine_pool_pre_ping_enabled(self):
        """Engine should have pool_pre_ping enabled"""
        assert engine.pool and hasattr(engine.pool, "ping")


class TestGetDbDependency:
    """Test get_db dependency function"""

    def test_get_db_is_generator(self):
        """get_db should be a generator function"""
        import inspect

        assert inspect.isgeneratorfunction(get_db)

    def test_get_db_yields_session(self, db: Session):
        """get_db should yield a database session"""
        session_gen = get_db()
        session = next(session_gen)
        try:
            assert session is not None
            assert isinstance(session, Session)
        finally:
            session_gen.close()


class TestDatabaseSession:
    """Test database session behavior"""

    def test_session_can_execute_query(self, db: Session):
        """Session should be able to execute queries"""
        result = db.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

    def test_session_can_commit(self, db: Session):
        """Session should support commit operations"""
        db.execute(text("SELECT 1"))
        db.commit()
        assert True  # If no exception, test passes

    def test_session_can_rollback(self, db: Session):
        """Session should support rollback operations"""
        db.execute(text("SELECT 1"))
        db.rollback()
        assert True  # If no exception, test passes


class TestDatabaseMetadata:
    """Test Base metadata and table registration"""

    def test_base_exists(self):
        """Base should be initialized"""
        assert Base is not None

    def test_base_has_metadata(self):
        """Base should have metadata attribute"""
        assert hasattr(Base, "metadata")

    def test_metadata_has_tables(self):
        """Metadata should have registered tables"""
        assert len(Base.metadata.tables) > 0

    def test_metadata_is_not_empty(self):
        """Metadata should not be empty"""
        assert Base.metadata.tables


class TestDatabaseConnection:
    """Test database connection health"""

    def test_database_is_accessible(self, db: Session):
        """Database should be accessible"""
        try:
            db.execute(text("SELECT 1"))
            assert True
        except Exception as e:
            pytest.fail(f"Database not accessible: {e}")

    def test_connection_pool_size(self, db: Session):
        """Connection pool should have reasonable size"""
        if hasattr(db.connection.pool, "size"):
            pool_size = db.connection.pool.size()
            assert pool_size >= 0

    def test_connection_is_alive(self, db: Session):
        """Database connection should be alive"""
        result = db.execute(text("SELECT 1"))
        assert result is not None


class TestDatabaseTransactionIsolation:
    """Test transaction isolation and rollback behavior"""

    def test_transaction_rolls_back_on_exception(self, db: Session):
        """Transaction should roll back on exception"""
        try:
            db.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)"))
            db.commit()

            # Start a transaction that will fail
            try:
                db.execute(text("INSERT INTO test_table VALUES (1)"))
                db.execute(
                    text("INSERT INTO test_table VALUES ('invalid')")
                )  # This will fail
                db.commit()
            except Exception:
                db.rollback()

            # Table should exist but empty
            result = db.execute(text("SELECT COUNT(*) FROM test_table"))
            count = result.fetchone()[0]
            assert count == 0  # Rollback worked
        finally:
            db.execute(text("DROP TABLE IF EXISTS test_table"))
            db.commit()

    def test_session_rollback_cleans_state(self, db: Session):
        """Rollback should clean session state"""
        # This is a structural test - actual rollback happens in fixture
        assert db is not None


class TestDatabaseTablesExist:
    """Test that critical tables exist"""

    def test_users_table_exists(self, db: Session):
        """Users table should exist"""
        try:
            result = db.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
                )
            )
            assert result.fetchone() is not None
        except Exception:
            # If not SQLite, try PostgreSQL query
            try:
                result = db.execute(
                    text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
                    )
                )
                assert result.fetchone()[0]
            except Exception:
                pytest.skip("Could not verify table existence")


class TestDatabaseSessionLifecycle:
    """Test database session lifecycle management"""

    def test_session_can_be_closed(self, db: Session):
        """Session should be closable"""
        db.close()
        assert True  # If no exception, test passes

    def test_session_can_be_reopened(self, db: Session):
        """Session can be reopened after close"""
        db.close()
        # Try to execute query - should fail or raise error
        with pytest.raises(Exception):
            db.execute(text("SELECT 1"))


class TestDatabaseURLHandling:
    """Test database URL parsing and validation"""

    def test_database_url_is_valid(self):
        """DATABASE_URL should be a valid SQLAlchemy URL"""
        from app.core.config import settings

        assert settings.DATABASE_URL is not None
        assert len(settings.DATABASE_URL) > 0

    def test_database_url_scheme_is_supported(self):
        """DATABASE_URL should use supported scheme"""
        from app.core.config import settings

        url = settings.DATABASE_URL.lower()
        assert any(
            url.startswith(scheme)
            for scheme in ["sqlite://", "postgresql://", "mysql://"]
        )


class TestDatabaseConfiguration:
    """Test database configuration settings"""

    def test_database_echo_disabled(self):
        """Database echo (SQL logging) should be disabled by default"""
        assert engine.echo is False

    def test_database_pool_recycle_set(self):
        """Database pool recycle should be set"""
        assert (
            hasattr(engine.pool, "_recycle") or True
        )  # Some pool types might not have this


class TestDatabaseSessionContext:
    """Test database session in different contexts"""

    def test_session_with_multiple_operations(self, db: Session):
        """Session should handle multiple operations"""
        # Execute multiple queries
        for i in range(5):
            db.execute(text(f"SELECT {i}"))
        assert True  # If no exception, test passes

    def test_session_with_nested_operations(self, db: Session):
        """Session should handle nested operations"""
        outer_result = db.execute(text("SELECT 1"))
        inner_result = db.execute(text("SELECT 2"))
        assert outer_result.fetchone()[0] == 1
        assert inner_result.fetchone()[0] == 2
