from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
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

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)
        self.symbol_map = {}
        self.records = None

    async def process_records(self, records):
        """Cleans and validates positions data before inserting into DB."""

        result = []
        for rec_type, recs in records.items():
            for record in recs:
                record['type'] = rec_type
                record['account'] = parms.DEF_ACCOUNT
                record['symbol_exchange'] = f'{record["tradingsymbol"]}:{record["exchange"]}'
                result.append(record)

        await self.delete_setup_table_records(result)
        self.records = result


service_positions = ServicePositions()
