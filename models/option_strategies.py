from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, JSON, Boolean, text, select


from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


def to_decimal(value, precision="0.01"):
    """Convert float to Decimal with given precision (default: 2 decimal places)."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


class OptionStrategies(Base):
    """Model to store option trading strategies and their risk-reward parameters."""
    __tablename__ = "option_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    strategy_name = Column(String, nullable=False)
    legs = Column(JSON, nullable=False)  # JSON format: [{"symbol": "NIFTY 18500 CE", "qty": -1}, {...}]
    max_profit = Column(DECIMAL(12, 2), nullable=True)  # 2 decimal precision for money values
    max_loss = Column(DECIMAL(12, 2), nullable=True)
    breakeven_points = Column(JSON, nullable=True)  # List of breakeven points
    source = Column(String, nullable=True, default="CODE")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    def __repr__(self):
        return f"<OptionStrategy {self.strategy_name} | Max PnL: {self.max_profit} | Max Loss: {self.max_loss}>"

    @classmethod
    async def get_all_results(cls, session, account_id=Env.ZERODHA_USERNAME):
        """Fetch all backtest results asynchronously."""
        result = await session.execute(select(cls).where(cls.account_id == account_id))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        """Convert API response data into an OptionStrategies instance."""
        return cls(strategy_name=data["strategy_name"], legs=data["legs"],  # JSON format is assumed correct
            max_profit=to_decimal(data.get("max_profit", 0.0)), max_loss=to_decimal(data.get("max_loss", 0.0)),
            breakeven_points=data.get("breakeven_points", []),  # Default to empty list
        )
