import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from models.option_strategies import OptionStrategies, Base

# Create an in-memory SQLite database for testing
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL)
SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="function")
def session():
    """Create a new database session for a test."""
    Base.metadata.create_all(engine)  # Create tables
    test_session = SessionTesting()
    yield test_session
    test_session.rollback()  # Rollback any changes after test
    test_session.close()


def test_insert_option_strategy(session):
    """Test inserting a new option strategy."""
    strategy = OptionStrategies(
        strategy_name="Iron Condor",
        legs=[{"symbol": "NIFTY 18500 CE", "qty": -1}, {"symbol": "NIFTY 18000 PE", "qty": -1}],
        max_profit=5000.0,
        max_loss=3000.0,
        breakeven_points=[18000.0, 18500.0],
        timestamp=datetime.now(timezone.utc),
    )

    session.add(strategy)
    session.commit()

    retrieved_strategy = session.query(OptionStrategies).filter_by(strategy_name="Iron Condor").first()
    assert retrieved_strategy is not None
    assert retrieved_strategy.max_profit == 5000.0
    assert retrieved_strategy.max_loss == 3000.0


def test_query_option_strategy(session):
    """Test querying an option strategy."""
    strategy = OptionStrategies(
        strategy_name="Bull Call Spread",
        legs=[{"symbol": "NIFTY 19000 CE", "qty": 1}, {"symbol": "NIFTY 19500 CE", "qty": -1}],
        max_profit=7000.0,
        max_loss=2000.0,
        breakeven_points=[19200.0],
        timestamp=datetime.now(timezone.utc),
    )

    session.add(strategy)
    session.commit()

    retrieved = session.query(OptionStrategies).filter_by(strategy_name="Bull Call Spread").first()
    assert retrieved is not None
    assert retrieved.legs == [{"symbol": "NIFTY 19000 CE", "qty": 1}, {"symbol": "NIFTY 19500 CE", "qty": -1}]


def test_delete_option_strategy(session):
    """Test deleting an option strategy."""
    strategy = OptionStrategies(
        strategy_name="Bear Put Spread",
        legs=[{"symbol": "NIFTY 19000 PE", "qty": 1}, {"symbol": "NIFTY 18500 PE", "qty": -1}],
        max_profit=6000.0,
        max_loss=2500.0,
        breakeven_points=[18750.0],
        timestamp=datetime.now(timezone.utc),
    )

    session.add(strategy)
    session.commit()

    session.delete(strategy)
    session.commit()

    retrieved = session.query(OptionStrategies).filter_by(strategy_name="Bear Put Spread").first()
    assert retrieved is None  # Ensure strategy is deleted
