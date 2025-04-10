from bidict import bidict

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Positions
from src.services.service_base import ServiceBase
from src.settings.constants_manager import load_env
from src.settings.parameter_manager import parms

logger = get_logger(__name__)

load_env()


class ServicePositions(SingletonBase, ServiceBase):
    """Service class for managing trading positions."""

    model = Positions
    conflict_cols = ['id']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)
        self.symbol_map = None
        self.records = None

    async def process_records(self, records):
        """Cleans and validates positions data before inserting into DB."""
        records = records.get("day", []) + records.get("net", [])
        for record in records:
            record['account'] = parms.DEF_ACCOUNT
            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'
        await self.delete_setup_table_records(records)

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



service_positions = ServicePositions()
