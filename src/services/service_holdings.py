from bidict import bidict

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
        self.position_map= None
        self.records = None

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

        # async def setup_table_records(self, default_records: List[Dict[str, Any]],
        #                               update_columns: Optional[List[str]] = None,
        #                               exclude_from_update=('timestamp',),
        #                               skip_update_if_exists: bool = False,
        #                               ignore_extra_columns: bool = False,  # <-- New flag
        #                               ) -> None:
        #     await super().setup_table_records(default_records,
        #                               update_columns,
        #                               exclude_from_update,
        #                               skip_update_if_exists,
        #                               ignore_extra_columns)
        #     market_state_manager.update_holdings(default_records)

service_holdings = ServiceHoldings()
