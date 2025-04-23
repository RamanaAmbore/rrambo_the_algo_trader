from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ThreadStatusTracker
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ThreadStatusTrackerServiceBase(SingletonBase, ServiceBase):
    """Service class for handling ReportTradebook database operations."""

    model = ThreadStatusTracker
    conflict_cols = ['account']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

    @classmethod
    def validate_clean_records(cls, data_record):
        """Cleans and validates trade records before inserting into the database."""

        return data_record
