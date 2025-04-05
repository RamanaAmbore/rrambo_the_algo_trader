from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Holdings
from src.services.service_base import ServiceBase
from src.settings.parameter_manager import parms

logger = get_logger(__name__)

class ServiceHoldings(SingletonBase, ServiceBase):
    """Service class for handling holdings database operations."""

    model = Holdings
    conflict_cols = ['tradingsymbol','exchange', 'account']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

    async def pre_process_records(self, holdings):
        await self.delete_all_records()
        master_rec = {'mtf_average_price': None, 'mtf_initial_margin': None, 'mtf_quantity': None,
                      'mtf_used_quantity': None, 'mtf_value': None}
        for holding in holdings:
            holding['account'] = parms.DEF_ACCOUNT
            mtf = holding.pop('mtf')
            if mtf is None:
                mtf = master_rec

            for k, v in mtf.items():
                holding[f'mtf_{k}'] = v
        return holdings


service_holdings = ServiceHoldings()
