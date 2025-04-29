from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models.watchlist_symbols import WatchlistSymbols
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceWatchlistSymbols(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = WatchlistSymbols
    conflict_cols = ['account', 'watchlist', 'tradingsymbol', 'exchange']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)

        self.records = None
        self.symbol_map = None

    async def process_records(self, records):
        """Cleans and validates positions data before inserting into DB."""

        result = []

        for record in records:
            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'
            result.append(record)

        await self.setup_table_records(result)
        self.records = result


service_watchlist_symbols = ServiceWatchlistSymbols()
