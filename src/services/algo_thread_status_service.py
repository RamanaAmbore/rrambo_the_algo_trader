from src.helpers.logger import get_logger
from src.models import AlgoThreadStatus
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = AlgoThreadStatus


class AlgoThreadStatusServiceBase(ServiceBase):
    """Service class for handling ReportTradebook database operations."""

    def __init__(self):
        super().__init__(model)

    @classmethod
    def validate_clean_records(cls, data_record):
        """Cleans and validates trade records before inserting into the database."""

        return data_record
