import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.access_token import AccessToken
from models.base import Base

# Test database URL (in-memory SQLite for isolated testing)
TEST_DB_URL = "sqlite:///:memory:"

# Set up test engine and session factory
engine = create_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db_session():
    """Fixture to create a fresh database for each test."""
    Base.metadata.create_all(engine)  # Create tables
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)  # Cleanup after test


def test_store_and_retrieve_access_token(db_session):
    """Test storing and retrieving a valid access token."""
    # Insert a new access token
    token_value = "test_token_123"
    new_token = AccessToken(token=token_value, timestamp=datetime.now(timezone.utc))
    db_session.add(new_token)
    db_session.commit()

    # Monkey-patch SessionLocal to use our test session
    AccessToken.SessionLocal = lambda: db_session

    # Retrieve stored token
    retrieved_token = AccessToken.get_stored_access_token()

    assert retrieved_token == token_value, "Stored token should match the inserted token."


def test_expired_access_token(db_session):
    """Test retrieving an expired access token (should return None)."""
    # Insert an expired token
    expired_token = AccessToken(
        token="expired_token",
        timestamp=datetime.now(timezone.utc) - timedelta(hours=25)  # Expired
    )
    db_session.add(expired_token)
    db_session.commit()

    # Monkey-patch SessionLocal to use our test session
    AccessToken.SessionLocal = lambda: db_session

    # Try fetching the token (should return None)
    assert AccessToken.get_stored_access_token() is None, "Expired tokens should not be returned."


def test_update_access_token(db_session):
    """Test updating an existing access token."""
    # Insert an initial token
    initial_token = AccessToken(token="old_token", timestamp=datetime.now(timezone.utc))
    db_session.add(initial_token)
    db_session.commit()

    # Monkey-patch SessionLocal to use our test session
    AccessToken.SessionLocal = lambda: db_session

    # Update the token
    AccessToken.check_update_access_token("new_token_456")

    # Verify the token is updated
    updated_token = db_session.query(AccessToken).first()
    assert updated_token.token == "new_token_456", "Token should be updated."
    assert updated_token.timestamp > initial_token.timestamp, "Timestamp should be updated."


def test_insert_new_access_token(db_session):
    """Test inserting a new access token when none exists."""
    # Ensure table is empty
    assert db_session.query(AccessToken).count() == 0

    # Monkey-patch SessionLocal to use our test session
    AccessToken.SessionLocal = lambda: db_session

    # Insert a new token
    AccessToken.check_update_access_token("fresh_token_789")

    # Verify new token is added
    stored_token = db_session.query(AccessToken).first()
    assert stored_token is not None, "A new token should be inserted."
    assert stored_token.token == "fresh_token_789", "Token value should match."
