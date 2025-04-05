from typing import Union, List

import pandas as pd

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ExchangeList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceExchangeList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ExchangeList

    conflict_cols = ['exchange']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)


service_exchange_list = ServiceExchangeList()
