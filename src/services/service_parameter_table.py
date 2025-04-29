from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ParameterTable
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceParameterTable(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ParameterTable
    conflict_cols = ['account', 'parameter']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)


# Singleton instance
service_parameter_table = ServiceParameterTable()
