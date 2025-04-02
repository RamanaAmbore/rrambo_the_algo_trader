import logging

from src.models import WatchList
from src.services.service_base import ServiceBase

logger = logging.getLogger(__name__)


class ServiceWatchList(ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    _instance = None
    model = WatchList
    conflict_cols = ['watchlist', 'account']

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ServiceWatchList, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Ensure __init__ is only called once."""
        if not hasattr(self, "_initialized"):  # Ensure _initialized is instance-scoped
            super().__init__(self.model, self.conflict_cols)
            self._initialized = True  # Mark as initialized


# Singleton instance
service_watch_list = ServiceWatchList()
