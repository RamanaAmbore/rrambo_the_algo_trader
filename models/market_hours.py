from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, DateTime, Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.config_loader import sc
from .base import Base


class MarketHours(Base):
    __tablename__ = "market_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_date = Column(DateTime, unique=True, nullable=True)  # Nullable for default record
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_default = Column(Boolean, default=False)  # Mark as default record

    @classmethod
    async def get_market_hours(cls, session: AsyncSession):
        """Retrieve today's market hours or fallback to default hours."""
        today = datetime.utcnow()

        # First, try to fetch today's market hours
        query = select(cls).where(cls.market_date == today)
        result = await session.execute(query)
        market_hours = result.scalars().first()

        if not market_hours:
            # Fetch default market hours if today's is not found
            query = select(cls).where(cls.is_default == True)
            result = await session.execute(query)
            market_hours = result.scalars().first()

        return market_hours

    @classmethod
    async def set_default_market_hours(cls, session: AsyncSession):
        """Ensure there is a default market hours record in the database."""
        query = select(cls).where(cls.is_default == True)
        result = await session.execute(query)
        existing_default = result.scalars().first()

        if not existing_default:
            market_start = datetime.combine(datetime.now(tz=ZoneInfo(sc.indian_timezone)).date(), time(9, 15))
            market_end = datetime.combine(datetime.now(tz=ZoneInfo(sc.indian_timezone)).date(), time(15, 30))

            default_market_hours = cls(
                market_date=None, start_time=market_start, end_time=market_end, is_default=True
            )
            session.add(default_market_hours)
            await session.commit()
