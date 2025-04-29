from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import InstrumentList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceInstrumentList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = InstrumentList
    conflict_cols = ['tradingsymbol', 'exchange']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)

    async def process_records(self, records):
        """Cleans and validates trade records before inserting into the database."""
        # Ensure expiry column is handled properly
        for record in records:
            if record['expiry'] == '':
                record['expiry'] = None
            record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'

        await self.delete_setup_table_records(records,batch_size=500)


service_instrument_list = ServiceInstrumentList()
