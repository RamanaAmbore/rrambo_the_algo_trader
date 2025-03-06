from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, DateTime, DECIMAL, ForeignKey, text, String, Boolean, select

from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


def to_decimal(value, precision="0.0001"):
    """Convert float to Decimal with 4 decimal places for option Greeks."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


class OptionGreeks(Base):
    """Model to store option Greeks such as Delta, Theta, Vega, Gamma, and IV."""
    __tablename__ = "option_greeks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    instrument_token = Column(Integer, ForeignKey("option_contracts.instrument_token", ondelete="CASCADE"),
                              nullable=False)
    delta = Column(DECIMAL(10, 4), nullable=True)  # Higher precision for Greeks
    theta = Column(DECIMAL(10, 4), nullable=True)
    vega = Column(DECIMAL(10, 4), nullable=True)
    gamma = Column(DECIMAL(10, 4), nullable=True)
    iv = Column(DECIMAL(10, 2), nullable=True)  # IV typically has 2 decimal places
    source = Column(String, nullable=True, default="CODE")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    def __repr__(self):
        return f"<OptionGreek Token: {self.instrument_token} | Δ: {self.delta} | IV: {self.iv}>"

    @classmethod
    async def get_all_results(cls, session, account_id=Env.ZERODHA_USERNAME):
        """Fetch all backtest results asynchronously."""
        result = await session.execute(select(cls).where(cls.account_id == account_id))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        """Convert API response data into an OptionGreeks instance."""
        return cls(instrument_token=int(data["instrument_token"]), delta=to_decimal(data.get("delta", 0.0)),
                   theta=to_decimal(data.get("theta", 0.0)), vega=to_decimal(data.get("vega", 0.0)),
                   gamma=to_decimal(data.get("gamma", 0.0)), iv=to_decimal(data.get("iv", 0.0), precision="0.01"),
                   # IV needs 2 decimal places
                   )
