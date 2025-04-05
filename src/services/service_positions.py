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

    async def process_records(self, records):
        """Cleans and validates positions data before inserting into DB."""
        await self.delete_all_records()
        records = records.get("day", []) + records.get("net", [])
        for record in records:
            record['account'] = parms.DEF_ACCOUNT
        await self.setup_table_records(records)


service_positions = ServicePositions()
