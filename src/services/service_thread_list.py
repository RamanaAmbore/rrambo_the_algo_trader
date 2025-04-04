import logging

from src.core.singleton_base import SingletonBase
from src.models import ThreadList
from src.services.service_base import ServiceBase

logger = logging.getLogger(__name__)


class ServiceThreadList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ThreadList
    conflict_cols = ['thread']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)


# Singleton instance
service_thread_list = ServiceThreadList()
