from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ThreadSchedule
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceThreadSchedule(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ThreadSchedule
    conflict_cols = ['thread', 'schedule']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)


# Singleton instance
service_thread_schedule = ServiceThreadSchedule()
