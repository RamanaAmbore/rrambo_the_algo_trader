from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Holdings
from src.services.service_base import ServiceBase
from src.settings.parameter_manager import parms

logger = get_logger(__name__)


class ServiceHoldings(SingletonBase, ServiceBase):
    """Service class for handling holdings database operations."""

    model = Holdings
    conflict_cols = ['tradingsymbol', 'exchange', 'account']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)
        self.symbol_map = {}
        self.records = []

    async def process_records(self, records):

        master_rec = {'mtf_average_price': None, 'mtf_initial_margin': None, 'mtf_quantity': None,
                      'mtf_used_quantity': None, 'mtf_value': None}
        for record in records:
            record['account'] = parms.DEF_ACCOUNT
            mtf = record.pop('mtf')
            if mtf is None:
                mtf = master_rec

            for k, v in mtf.items():
                record[f'mtf_{k}'] = v

            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'
        await self.delete_setup_table_records(records)
        self.records = records

    async def get_symbol_map(self):
        if not self.symbol_map:
            await self.get_all_records(only_when_empty=True)

            for record in self.records:
                if record.symbol_exchange and record.instrument_token is not None:
                    self.symbol_map[record.symbol_exchange] = record.instrument_token


service_holdings = ServiceHoldings()
