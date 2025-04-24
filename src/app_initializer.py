import asyncio

from src.app_state_manager import app_state
from src.core.decorators import track_it
from src.core.report_downloader import ReportDownloader
from src.core.report_uploader import ReportUploader
from src.core.singleton_base import SingletonBase
from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.date_time_utils import today_indian, current_time_indian
from src.helpers.logger import get_logger
from src.market_ticker import MarketTicker
from src.services.service_access_tokens import service_access_tokens
from src.services.service_broker_accounts import service_broker_accounts
from src.services.service_exchange_list import service_exchange_list
from src.services.service_holdings import service_holdings
from src.services.service_instrument_list import service_instrument_list
from src.services.service_parameter_table import service_parameter_table
from src.services.service_positions import service_positions
from src.services.service_schedule_list import service_schedule_list
from src.services.service_schedule_time import service_schedule_time
from src.services.service_thread_list import service_thread_list
from src.services.service_thread_schedule import service_thread_schedule
from src.services.service_watchlist import service_watchlist
from src.services.service_watchlist_symbols import service_watchlist_symbols
from src.settings.constants_manager import DEF_PARAMETERS, DEF_BROKER_ACCOUNTS, DEF_ACCESS_TOKENS, DEF_THREAD_LIST, \
    DEF_SCHEDULES, DEF_WATCH_LIST, DEF_EXCHANGE_LIST, DEF_THREAD_SCHEDULE, DEF_SCHEDULE_TIME, DEF_WATCHLIST_SYMBOLS
from src.settings.parameter_manager import refresh_parameters, parms

logger = get_logger(__name__)


class AppInitializer(SingletonBase):
    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.kite_obj = None
        self.kite_conn = None
        self.start_time = None
        self.end_time = None

    @track_it()
    async def setup(self):

        # Step 1: Set up broker and parameter records
        await service_broker_accounts.setup_table_records(DEF_BROKER_ACCOUNTS, skip_update_if_exists=True)
        await service_parameter_table.setup_table_records(DEF_PARAMETERS, skip_update_if_exists=True)

        # Step 2: Set up access token records
        await service_access_tokens.setup_table_records(DEF_ACCESS_TOKENS, skip_update_if_exists=True)

        # Step 3: Refresh parameters
        records = await service_parameter_table.get_all_records()
        refresh_parameters(records, refresh=True)

        await asyncio.gather(
            service_schedule_list.setup_table_records(DEF_SCHEDULES, skip_update_if_exists=True),
            service_exchange_list.setup_table_records(DEF_EXCHANGE_LIST, skip_update_if_exists=True)
        )
        await service_schedule_time.setup_table_records(DEF_SCHEDULE_TIME, skip_update_if_exists=True)
        service_schedule_time.get_market_schedule_recs_for_today()

        # Step 4: Initialize singleton instance
        ZerodhaKiteConnect().get_kite_conn(test_conn=True)
        is_open = False

        if parms.DROP_TABLES:
            await self.setup_pre_market()
        else:
            is_open, self.start_time, self.end_time = service_schedule_time.is_market_open(pre_market=True)

        if is_open:
            await app_initializer.setup_pre_market()

        await service_positions.process_records(
            await asyncio.to_thread(app_initializer.get_kite_conn().positions)
        )

        await service_positions.process_records(
            await asyncio.to_thread(app_initializer.get_kite_conn().positions)
        )

        await self.update_app_sate()

    @track_it()
    async def setup_pre_market(self):
        await asyncio.gather(
            service_thread_list.setup_table_records(DEF_THREAD_LIST, skip_update_if_exists=True),
            service_watchlist.setup_table_records(DEF_WATCH_LIST, skip_update_if_exists=True),
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

        await service_watchlist_symbols.process_records(DEF_WATCHLIST_SYMBOLS)

    @track_it()
    async def update_app_sate(self):
        app_state.set_schedule_time(service_schedule_time.get_schedule_records())
        app_state.set_instruments(await service_instrument_list.get_record_map(key_attr='symbol_exchange'))

        app_state.set_positions(await service_positions.get_record_map())
        app_state.set_holdings(await service_holdings.get_record_map())
        app_state.set_watchlist(await service_watchlist_symbols.get_record_map())

        app_state.set_track_list(service_schedule_time.get_unique_exchanges())

        market_ticker = MarketTicker(app_initializer.get_kite_obj(), self.start_time['start_time'], self.end_time['end_time'])
        market_ticker.add_instruments(app_state.track_instr_set)  # Add tokens
        market_ticker.start()

        logger.info("hello world!")

    @staticmethod
    async def sync_reports():
        await asyncio.to_thread(ReportDownloader.login_download_reports)
        await ReportUploader.upload_reports()

    @staticmethod
    def get_kite_conn():
        return ZerodhaKiteConnect().get_kite_conn()

    @staticmethod
    def get_kite_obj():
        return ZerodhaKiteConnect()



app_initializer = AppInitializer()
