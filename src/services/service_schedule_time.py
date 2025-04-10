from typing import List, Optional, Union, Tuple, Set

from sqlalchemy import select

from src.core.singleton_base import SingletonBase
from src.helpers.database_manager import db
from src.helpers.date_time_utils import today_indian
from src.helpers.logger import get_logger
from src.models.schedule_time import ScheduleTime
from src.services.service_base import ServiceBase

logger = get_logger(__name__)
class ServiceScheduleTime(SingletonBase, ServiceBase):
    """Service class for handling ScheduleTime database operations."""

    _instance = None
    model = ScheduleTime
    conflict_cols = ['schedule', 'market_day', 'exchange', 'start_time']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

    def _get_unique_exchanges(self):
        """Fetch unique exchange values from the table."""
        exchanges = set()
        with db.get_sync_session() as session:
            try:
                # Assuming 'exchange' is a column in your model
                query = select(self.model.exchange).distinct()
                results = session.execute(query).scalars().all()
                return results
            except Exception as e:
                logger.error(f"Error fetching unique exchanges: {e}")
                return ["*"]  # Fallback to global if error


    def get_market_hours_for_today(self) -> List:
        """Retrieve today's market hours with a fallback mechanism, considering all exchanges."""
        today = today_indian()
        weekday = today.strftime("%A")
        today_str = today.strftime("%Y-%m-%d")  # Assuming default postgres date format is<\ctrl3348>-MM-DD
        records= []
        exchanges = self._get_unique_exchanges()
        imp_columns = self.conflict_cols+['end_time','is_market_open']
        with db.get_sync_session() as session:
            for schedule in ('MARKET', 'PRE_MARKET'):
                for exchange in exchanges:
                    logger.info(f"Checking for {schedule} hours for {today_str} with exchange '{exchange}'")
                    query = select(self.model).where(
                        self.model.market_day == today_str,
                        self.model.schedule == schedule,
                        self.model.exchange == exchange
                    )
                    record = session.execute(query).scalars().first()
                    if not record:
                        logger.info(
                            f"Checking default weekday {schedule} hours for {weekday} with exchange '{exchange}'")
                        query = select(self.model).where(
                            self.model.market_day == weekday,
                            self.model.schedule == schedule,
                            self.model.exchange == exchange
                        )
                        record = session.execute(query).scalars().first()
                    if not record:
                        logger.info(
                            f"Checking default weekday {schedule} hours for * with exchange '{exchange}'")
                        query = select(self.model).where(
                            self.model.market_day == '*',
                            self.model.schedule == schedule,
                            self.model.exchange == exchange
                        )
                        record = session.execute(query).scalars().first()
                    if record:
                        result = {column: getattr(record, column) for column in imp_columns}
                        records.append(result)
        return records  # Return a unique list of matching schedules

    def get_batch_schedules(self, batch_type: Optional[Union[str, List[str], Tuple[str], Set[str]]] = None) -> List:
        """Retrieve today's batch processing schedule_list, considering all exchanges."""
        today = today_indian()
        today_str = today.strftime("%Y-%m-%d")  # Assuming default postgres date format is<\ctrl3348>-MM-DD
        all_schedules = []
        exchanges = self._get_unique_exchanges()

        with db.get_sync_session() as session:
            for exchange in exchanges:
                logger.info(
                    f"Checking batch schedule_list of type {batch_type} for {today_str} with exchange '{exchange}'")
                query = select(self.model).where(self.model.market_date == today_str)

                if batch_type:
                    query = query.where(self.model.schedule.in_(batch_type))

                query = query.where(self.model.exchange == exchange)

                found_schedules = session.execute(query).scalars().all()
                if found_schedules:
                    all_schedules.extend(found_schedules)

            # Fetch global batch schedules (exchange '*') once
            logger.info(f"Checking batch schedule_list of type {batch_type} for {today_str} with global exchange")
            query = select(self.model).where(self.model.market_date == today_str)

            if batch_type:
                query = query.where(self.model.schedule.in_(batch_type))

            query = query.where(self.model.exchange == "*")

            found_schedules = session.execute(query).scalars().all()
            if found_schedules:
                all_schedules.extend(found_schedules)

            if not all_schedules:
                logger.info(f"No batch schedule_list found for {batch_type} on {today_str} for any exchange")

        return list(set(all_schedules))


service_schedule_time = ServiceScheduleTime()
