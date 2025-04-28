from src.core.decorators import singleton_init_guard
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ScheduleList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceScheduleList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ScheduleList
    conflict_cols = ['schedule']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)


# Singleton instance
service_schedule_list = ServiceScheduleList()
