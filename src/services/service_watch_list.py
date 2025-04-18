from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import WatchList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceWatchList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = WatchList
    conflict_cols = ['watchlist', 'account']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)
        self.records = None
        self.symbol_map = None


# Singleton instance
service_watch_list = ServiceWatchList()
