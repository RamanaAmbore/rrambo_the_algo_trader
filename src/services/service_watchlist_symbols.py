from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models.watchlist_symbols import WatchlistSymbols
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceWatchlistSymbols(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = WatchlistSymbols
    conflict_cols = ['account', 'watchlist', 'tradingsymbol', 'exchange']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

        self.records = None
        self.symbol_map = None

    async def process_records(self, records):
        """Cleans and validates positions data before inserting into DB."""

        result = []

        for record in records:
            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'
            result.append(record)

        await self.delete_setup_table_records(result)
        self.records = result


service_watchlist_symbols = ServiceWatchlistSymbols()
