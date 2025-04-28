from src.core.decorators import singleton_init_guard
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ThreadStatusTracker
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ThreadStatusTrackerServiceBase(SingletonBase, ServiceBase):
    """Service class for handling ReportTradebook database operations."""

    model = ThreadStatusTracker
    conflict_cols = ['account']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)

    @classmethod
    def validate_clean_records(cls, data_record):
        """Cleans and validates trade records before inserting into the database."""

        return data_record
