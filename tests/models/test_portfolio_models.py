import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models.base import Base
from models.portfolio_holdings import PortfolioHoldings


# Create an in-memory SQLite database for testing
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

@pytest.fixture(scope="function")
def db_session():
    """Fixture to create and teardown an in-memory database session for testing."""
    Base.metadata.create_all(engine)  # Create tables
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


def test_create_portfolio_holding(db_session):
    """Test adding a new portfolio holding."""
    holding = PortfolioHoldings(
        trading_symbol="RELIANCE",
        quantity=10,
        average_price=2500.0,
        current_price=2550.0,
        pnl=500.0
    )
    db_session.add(holding)
    db_session.commit()

    stored_holding = db_session.query(PortfolioHoldings).filter_by(trading_symbol="RELIANCE").first()
    assert stored_holding is not None
    assert stored_holding.trading_symbol == "RELIANCE"
    assert stored_holding.quantity == 10
    assert stored_holding.average_price == 2500.0
    assert stored_holding.current_price == 2550.0
    assert stored_holding.pnl == 500.0
    assert isinstance(stored_holding.timestamp, datetime)  # Ensure timestamp is set


def test_update_portfolio_holding(db_session):
    """Test updating a portfolio holding."""
    holding = PortfolioHoldings(
        trading_symbol="TCS",
        quantity=5,
        average_price=3500.0,
        current_price=3550.0,
        pnl=250.0
    )
    db_session.add(holding)
    db_session.commit()

    # Update the record
    holding.current_price = 3600.0
    holding.pnl = 500.0
    db_session.commit()

    updated_holding = db_session.query(PortfolioHoldings).filter_by(trading_symbol="TCS").first()
    assert updated_holding.current_price == 3600.0
    assert updated_holding.pnl == 500.0


def test_delete_portfolio_holding(db_session):
    """Test deleting a portfolio holding."""
    holding = PortfolioHoldings(
        trading_symbol="INFY",
        quantity=8,
        average_price=1500.0,
        current_price=1520.0,
        pnl=160.0
    )
    db_session.add(holding)
    db_session.commit()

    # Delete the record
    db_session.delete(holding)
    db_session.commit()

    deleted_holding = db_session.query(PortfolioHoldings).filter_by(trading_symbol="INFY").first()
    assert deleted_holding is None
