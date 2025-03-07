import datetime
from datetime import datetime

from sqlalchemy import Column, DateTime, text

from models import StockList
from utils.date_time_utils import timestamp_indian
from utils.db_connection import DbConnection as Db

def save_stock_list(sync=False):
    with Db.get_session(sync) as session:
        last_update = session.query(StockList).order_by(StockList.last_updated.desc()).first()
        if last_update and (datetime.date.today() - last_update.last_updated).days < 7:
            session.close()
            return

        session.query(StockList).delete()
        for stock in []:
            session.add(StockList(symbol=stock["symbol"], name=stock["name"], yahoo_ticker=stock["yahoo_ticker"],
                                  exchange=stock["exchange"],
                                  timestamp=Column(DateTime(timezone=True), default=timestamp_indian,
                                                   server_default=text("CURRENT_TIMESTAMP")), ))
        session.commit()
