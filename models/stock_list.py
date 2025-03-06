import datetime
from datetime import datetime

from sqlalchemy import Column, String, DateTime, text, Boolean
from sqlalchemy import Date

from utils.settings_loader import Env
from utils.date_time_utils import timestamp_indian
from .base import Base


# Define Stock List Table
class StockList(Base):
    __tablename__ = "stock_list"
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    symbol = Column(String, primary_key=True)
    name = Column(String)
    yahoo_ticker = Column(String)
    exchange = Column(String)
    last_updated = Column(Date)
    source = Column(String, nullable=True, default="SCHEDULE")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)


def save_stock_list(db_connection):
    with db_connection.sync_session() as session:
        last_update = session.query(StockList).order_by(StockList.last_updated.desc()).first()
        if last_update and (datetime.date.today() - last_update.last_updated).days < 7:
            session.close()
            return

        # kite = broker.kite
        # stocks = fetch_kite_stock_list(kite)

        session.query(StockList).delete()
        for stock in []:
            session.add(StockList(symbol=stock["symbol"], name=stock["name"], yahoo_ticker=stock["yahoo_ticker"],
                exchange=stock["exchange"], timestamp=Column(DateTime(timezone=True), default=timestamp_indian,
                                                             server_default=text("CURRENT_TIMESTAMP")), ))
        session.commit()
