import logging

from src.core.singleton_base import SingletonBase
from src.models import ScheduleList
from src.services.service_base import ServiceBase

logger = logging.getLogger(__name__)


class ServiceScheduleList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ScheduleList
    conflict_cols = ['schedule']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)


# Singleton instance
service_schedule_list = ServiceScheduleList()
