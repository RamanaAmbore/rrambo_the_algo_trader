from typing import List, Optional, Union, Tuple, Set

from sqlalchemy import select

from src.core.singleton_base import SingletonBase
from src.helpers.database_manager import db
from src.helpers.date_time_utils import today_indian, current_time_indian
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
        self.last_checked_date = None
        self.market_hours = None

    def _get_unique_exchanges(self) -> List[str]:
        """Fetch unique exchange values from the table."""
        with db.get_sync_session() as session:
            try:
                query = select(self.model.exchange).distinct()
                results = session.execute(query).scalars().all()
                return results
            except Exception as e:
                logger.error(f"Error fetching unique exchanges: {e}")
                return ["*"]

    def get_market_hours_for_today(self) -> List[dict]:
        """Retrieve today's market hours with a fallback mechanism, considering all exchanges."""
        if self.market_hours:
            return self.market_hours

        today = today_indian()
        weekday = today.strftime("%A")
        today_str = today.strftime("%Y-%m-%d")  # Assuming default postgres date format is YYYY-MM-DD
        records = []
        exchanges = self._get_unique_exchanges()
        imp_columns = self.conflict_cols + ['end_time', 'is_market_open']

        with db.get_sync_session() as session:
            for schedule in ('MARKET', 'PRE_MARKET'):
                for exchange in exchanges:
                    for market_day in [today_str, weekday, '*']:
                        logger.info(
                            f"Checking {schedule} hours for market_day='{market_day}' and exchange='{exchange}'"
                        )
                        query = select(self.model).where(
                            self.model.market_day == market_day,
                            self.model.schedule == schedule,
                            self.model.exchange == exchange
                        )
                        record = session.execute(query).scalars().first()
                        if record:
                            result = {column: getattr(record, column) for column in imp_columns}
                            records.append(result)
                            break  # Stop at first match for this combo

        self.market_hours = records
        return records

    def get_batch_schedules(
            self, batch_type: Optional[Union[str, List[str], Tuple[str], Set[str]]] = None
    ) -> List[ScheduleTime]:
        """Retrieve today's batch processing schedule list, considering all exchanges."""
        today_str = today_indian().strftime("%Y-%m-%d")
        all_schedules = []
        exchanges = self._get_unique_exchanges()

        with db.get_sync_session() as session:
            for exchange in exchanges + ["*"]:  # Handles global after loop
                logger.info(f"Checking batch schedules for {today_str} and exchange='{exchange}'")
                query = select(self.model).where(
                    self.model.market_date == today_str,
                    self.model.exchange == exchange
                )
                if batch_type:
                    query = query.where(self.model.schedule.in_(batch_type))

                found_schedules = session.execute(query).scalars().all()
                all_schedules.extend(found_schedules)

            if not all_schedules:
                logger.info(f"No batch schedules found for {batch_type} on {today_str} for any exchange.")

        return list({sched.id: sched for sched in all_schedules}.values())  # Deduplication by ID

    def is_market_open(
            self, pre_market: bool = False, exchange: str = '*'
    ) -> Tuple[bool, Optional[dict], Optional[dict]]:
        """Determine if the market is currently open."""
        today = today_indian()
        current_time = current_time_indian()
        market_flag = 'PRE_MARKET' if pre_market else 'MARKET'

        if self.last_checked_date != today or self.market_hours is None:
            try:
                self.market_hours = self.get_market_hours_for_today()
                self.last_checked_date = today
            except Exception as e:
                logger.error(f"Failed to fetch market hours: {e}")
                self.market_hours = None
                return False, None, None

        filtered = [
            x for x in self.market_hours
            if x.get('schedule') == market_flag and x.get('exchange') == exchange and x.get('is_market_open')
        ]

        if not filtered:
            return False, None, None

        earliest_start = min(filtered, key=lambda x: x.get('start_time'))
        latest_end = max(filtered, key=lambda x: x.get('end_time'))

        is_open = earliest_start.get('start_time') <= current_time <= latest_end.get('end_time')
        return is_open, earliest_start, latest_end

# Singleton instance
service_schedule_time = ServiceScheduleTime()