import asyncio
import inspect

from src.core.decorators import track_exec_time
from src.core.report_downloader import ReportDownloader
from src.core.report_uploader import ReportUploader
from src.core.singleton_base import SingletonBase
from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_access_tokens import service_access_tokens
from src.services.service_broker_accounts import service_broker_accounts
from src.services.service_exchange_list import service_exchange_list
from src.services.service_holdings import service_holdings
from src.services.service_instrument_list import service_instrument_list
from src.services.service_parameter_table import service_parameter_table
from src.services.service_schedule_list import service_schedule_list
from src.services.service_schedule_time import service_schedule_time
from src.services.service_thread_list import service_thread_list
from src.services.service_thread_schedule import service_thread_schedule
from src.services.service_watch_list import service_watch_list
from src.services.service_watch_list_instruments import service_watch_list_instruments
from src.settings.constants_manager import DEF_PARAMETERS, DEF_BROKER_ACCOUNTS, DEF_ACCESS_TOKENS, DEF_THREAD_LIST, \
    DEF_SCHEDULES, DEF_WATCH_LIST, DEF_EXCHANGE_LIST, DEF_THREAD_SCHEDULE, DEF_SCHEDULE_TIME, DEF_WATCH_LIST_INSTRUMENTS
from src.settings.parameter_manager import refresh_parameters

logger = get_logger(__name__)


class AppInitializer(SingletonBase):
    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.kite_obj = None
        self.kite_conn = None

    @track_exec_time()
    async def setup_parameters(self):

        # Step 1: Set up broker and parameter records
        await service_broker_accounts.setup_table_records(DEF_BROKER_ACCOUNTS, skip_update_if_exists=True)
        await service_parameter_table.setup_table_records(DEF_PARAMETERS, skip_update_if_exists=True)

        # Step 2: Set up access token records
        await service_access_tokens.setup_table_records(DEF_ACCESS_TOKENS, skip_update_if_exists=True)

        # Step 3: Refresh parameters
        records = await service_parameter_table.get_all_records()
        refresh_parameters(records, refresh=True)

        # Step 4: Initialize singleton instance
        ZerodhaKiteConnect().get_kite_conn(test_conn=True)

    @track_exec_time()
    async def setup_pre_market(self):
        await asyncio.gather(
            service_thread_list.setup_table_records(DEF_THREAD_LIST, skip_update_if_exists=True),
            service_schedule_list.setup_table_records(DEF_SCHEDULES, skip_update_if_exists=True),
            service_watch_list.setup_table_records(DEF_WATCH_LIST, skip_update_if_exists=True),
            service_exchange_list.setup_table_records(DEF_EXCHANGE_LIST, skip_update_if_exists=True)
        )
        await asyncio.gather(
            service_thread_schedule.setup_table_records(DEF_THREAD_SCHEDULE, skip_update_if_exists=True),
            service_schedule_time.setup_table_records(DEF_SCHEDULE_TIME, skip_update_if_exists=True),
        )

        instrument_list = await asyncio.to_thread(self.get_kite_conn().instruments)  # Run in a separate thread

        exchange_list = {record["exchange"] for record in instrument_list}
        exchange_list = tuple({'exchange': record} for record in exchange_list)
        await service_exchange_list.setup_table_records(exchange_list)

        await service_instrument_list.process_records(instrument_list)

        # positions = await asyncio.to_thread(get_kite_conn().positions)
        holdings = await asyncio.to_thread(self.get_kite_conn().holdings)

        await asyncio.gather(
            # service_positions.process_records(positions),
            service_holdings.process_records(holdings),
        )
        await service_watch_list_instruments.setup_table_records(DEF_WATCH_LIST_INSTRUMENTS, skip_update_if_exists=True)

    @staticmethod
    async def sync_reports():
        await asyncio.to_thread(ReportDownloader.login_download_reports)
        await ReportUploader.upload_reports()
    @staticmethod
    def get_kite_conn():
        return ZerodhaKiteConnect().get_kite_conn()

    @staticmethod
    def get_kite_obj(self):
        return ZerodhaKiteConnect()

app_initializer = AppInitializer()
