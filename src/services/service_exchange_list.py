from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ExchangeList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceExchangeList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ExchangeList

    conflict_cols = ['exchange']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)


service_exchange_list = ServiceExchangeList()
