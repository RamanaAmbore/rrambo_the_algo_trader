import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.orders import Trades, Orders

# Setup in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope="module")
def setup_db():
    """Create tables and provide a database session."""
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_insert_trade(setup_db):
    """Test inserting a trade record."""
    session = setup_db
    trade = Trades(
        trade_id="T12345",
        trading_symbol="RELIANCE",
        exchange="NSE",
        transaction_type="BUY",
        quantity=10,
        price=2500.0,
        timestamp=datetime.utcnow()
    )
    session.add(trade)
    session.commit()

    fetched_trade = session.query(Trades).filter_by(trade_id="T12345").first()
    assert fetched_trade is not None
    assert fetched_trade.trading_symbol == "RELIANCE"
    assert fetched_trade.quantity == 10

def test_insert_order_history(setup_db):
    """Test inserting an order history record."""
    session = setup_db
    order = Orders(
        order_id="O67890",
        trading_symbol="INFY",
        exchange="NSE",
        status="COMPLETED",
        order_type="MARKET",
        quantity=5,
        price=1500.5,
        timestamp=datetime.utcnow()
    )
    session.add(order)
    session.commit()

    fetched_order = session.query(Orders).filter_by(order_id="O67890").first()
    assert fetched_order is not None
    assert fetched_order.trading_symbol == "INFY"
    assert fetched_order.status == "COMPLETED"

def test_trade_timestamp(setup_db):
    """Ensure the default timestamp is set correctly."""
    session = setup_db
    trade = Trades(
        trade_id="T54321",
        trading_symbol="TCS",
        exchange="NSE",
        transaction_type="SELL",
        quantity=15,
        price=3800.0
    )
    session.add(trade)
    session.commit()

    fetched_trade = session.query(Trades).filter_by(trade_id="T54321").first()
    assert fetched_trade is not None
    assert isinstance(fetched_trade.timestamp, datetime)
    assert fetched_trade.timestamp <= datetime.utcnow() + timedelta(seconds=1)  # Timestamp should be recent

