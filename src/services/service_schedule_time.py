from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.singleton_base import SingletonBase
from src.helpers.database_manager import db
from src.helpers.date_time_utils import today_indian
from src.helpers.logger import get_logger
from src.models.schedule_time import ScheduleTime
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = ScheduleTime


class ServiceScheduleTime(SingletonBase, ServiceBase):
    """Service class for handling ScheduleTime database operations."""

    _instance = None
    model = ScheduleTime
    conflict_cols = ['schedule', 'market_date', 'exchange', 'weekday', 'start_time']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

    def get_market_hours_for_today(self):
        """Retrieve today's market hours with a fallback mechanism."""
        today = today_indian()
        weekday = today.strftime("%A")

        with db.get_sync_session() as session:
            logger.info(f"Checking for MARKET hours for {today}")

            query = select(self.model).where(self.model.market_date == today,
                                             self.model.schedule == "MARKET")
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info(f"Checking default weekday MARKET hours for {weekday}")
            query = select(self.model).where(self.model.weekday == weekday,
                                             self.model.schedule == "MARKET")
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info("Checking for GLOBAL default MARKET hours")
            query = select(self.model).where(self.model.weekday == "GLOBAL",
                                             self.model.schedule == "MARKET")
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

        return None  # Return None if no matching schedule is found

    def get_batch_schedules(self, session: Session, batch_type=None):
        """Retrieve today's batch processing schedule_list."""
        today = today_indian()

        if batch_type and not isinstance(batch_type, (list, tuple, set)):
            batch_type = [batch_type]

        schedule_list = []

        logger.info(f"Checking batch schedule_list of type {batch_type} for {today}")

        query = select(self.model).where(self.model.market_date == today,
                                         self.model.schedule == "MARKET")
        if batch_type:
            query = query.where(self.model.schedule.in_(batch_type))

        found_schedules = session.execute(query).scalars().all()
        if found_schedules:
            schedule_list.extend(found_schedules)

        if not schedule_list:
            logger.info(f"No batch schedule_list found for {batch_type} on {today}")

        return schedule_list  # Return list instead of None


service_schedule_time = ServiceScheduleTime()
