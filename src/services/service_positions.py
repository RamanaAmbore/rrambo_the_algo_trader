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
        self.symbol_map = {}
        self.records = None

    async def process_records(self, records):
        """Cleans and validates positions data before inserting into DB."""
        records = records.get("day", []) + records.get("net", [])
        for record in records:
            record['account'] = parms.DEF_ACCOUNT
            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'
        await self.delete_setup_table_records(records)
        self.records = records

    async def get_symbol_map(self):
        if not self.symbol_map:
            await self.get_all_records(only_when_empty=False)
            for record in self.records:
                if record['symbol_exchange'] and record['instrument_token'] is not None:
                    self.symbol_map[record['symbol_exchange']] = record['instrument_token']

        return self.symbol_map


service_positions = ServicePositions()
