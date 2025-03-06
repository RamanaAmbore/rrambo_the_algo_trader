from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, text, Boolean, select

from utils.settings_loader import sc, Env
from utils.date_time_utils import timestamp_indian
from .base import Base


def to_decimal(value):
    """Convert float to Decimal with 2 decimal places."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class OptionContracts(Base):
    """Model to store available option contracts."""
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    instrument_token = Column(Integer, unique=True, nullable=False)
    trading_symbol = Column(String, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    strike_price = Column(DECIMAL(10, 2), nullable=False)  # 2 decimal places for precision
    option_type = Column(String, nullable=False)  # CE (Call) / PE (Put)
    lot_size = Column(Integer, nullable=False)
    tick_size = Column(DECIMAL(10, 2), nullable=False)  # Tick size needs exact precision
    source = Column(String, nullable=True, default="CODE")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    def __repr__(self):
        return f"<OptionContract {self.trading_symbol} | {self.option_type} | Strike {self.strike_price}>"

    @classmethod
    async def get_all_results(cls, session, account_id=Env.ZERODHA_USERNAME):
        """Fetch all backtest results asynchronously."""
        result = await session.execute(select(cls).where(cls.account_id == account_id))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        """Convert API response data into an OptionContracts instance."""
        return cls(instrument_token=int(data["instrument_token"]), trading_symbol=data["tradingsymbol"],
                   expiry_date=datetime.strptime(data["expiry"], "%Y-%m-%d").replace(
                       tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE)), strike_price=to_decimal(data["strike"]),
                   option_type=data["instrument_type"],  # CE / PE
                   lot_size=int(data["lot_size"]), tick_size=to_decimal(data["tick_size"]), )
