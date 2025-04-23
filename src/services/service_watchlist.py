from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Watchlist
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceWatchlist(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = Watchlist
    conflict_cols = ['watchlist', 'account']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)



# Singleton instance
service_watchlist = ServiceWatchlist()
