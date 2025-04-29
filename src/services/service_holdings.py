from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Holdings
from src.services.service_base import ServiceBase
from src.settings.parameter_manager import parms

logger = get_logger(__name__)


class ServiceHoldings(SingletonBase, ServiceBase):
    """Service class for handling holdings database operations."""

    model = Holdings
    conflict_cols = ['tradingsymbol', 'exchange', 'account']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

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


service_holdings = ServiceHoldings()
