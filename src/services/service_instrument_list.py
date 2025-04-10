from bidict import bidict

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import InstrumentList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceInstrumentList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = InstrumentList
    conflict_cols = ['tradingsymbol', 'exchange']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)
        self.records = None
        self.symbol_map = None

    async def process_records(self, records):
        """Cleans and validates trade records before inserting into the database."""
        # Ensure expiry column is handled properly
        for record in records:
            if record['expiry'] == '':
                record['expiry'] = None
            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'

        await self.setup_table_records(records)

    async def get_symbol_map(self):
        # Await the call to fetch all records
        await self.get_all_records()

        # Build a bidirectional map: symbol_exchange <-> instrument_token
        self.symbol_map = bidict({
            record.symbol_exchange: record.instrument_token
            for record in self.records
            if record.symbol_exchange and record.instrument_token is not None
        })

        return self.symbol_map

    async def get_all_records(self):
        # Await the call to fetch all records
        if self.records is None:
            self.records = await self.get_all_records()
        return self.records


service_instrument_list = ServiceInstrumentList()
