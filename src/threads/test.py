# You should run the async function inside an event loop (e.g., in an async main function)
import asyncio

from src.core.app_initializer import setup_parameters, get_kite_conn
from src.core.decorators import track_exec_time
from src.core.report_downloader import ReportDownloader
# from src.core.report_downloader import ReportDownloader
from src.core.report_uploader import ReportUploader
from src.services.service_watch_list_instruments import service_watch_list_instruments
from src.services.service_exchange_list import service_exchange_list
from src.services.service_holdings import service_holdings
from src.services.service_instrument_list import service_instrument_list
from src.services.service_positions import service_positions
from src.services.service_schedule_list import service_schedule_list
from src.services.service_schedule_time import service_schedule_time
from src.services.service_thread_list import service_thread_list
from src.services.service_thread_schedule import service_thread_schedule
from src.services.service_watch_list import service_watch_list
from src.settings.constants_manager import DEF_THREAD_LIST, DEF_SCHEDULES, DEF_THREAD_SCHEDULE, DEF_EXCHANGE_LIST, \
    DEF_SCHEDULE_TIME, DEF_WATCH_LIST, DEF_WATCH_LIST_INSTRUMENTS


@track_exec_time()
async def run():
    """Main execution function, running all tasks in parallel."""

    await setup_parameters()

    # await asyncio.gather(
    #     service_thread_list.setup_table_records(DEF_THREAD_LIST, skip_update_if_exists=True),
    #     service_schedule_list.setup_table_records(DEF_SCHEDULES, skip_update_if_exists=True),
    #     # service_watch_list.setup_table_records(DEF_WATCH_LIST, skip_update_if_exists=True),
    # )
    #
    # await service_thread_schedule.setup_table_records(DEF_THREAD_SCHEDULE, skip_update_if_exists=True)
    #
    # instrument_list = await asyncio.to_thread(get_kite_conn().instruments)  # Run in a separate thread
    # await service_instrument_list.process_records(instrument_list)
    #
    # exchange_list = {record["exchange"] for record in instrument_list}
    # exchange_list = tuple({'exchange': record} for record in exchange_list)
    #
    # await asyncio.gather(
    #     service_exchange_list.setup_table_records(DEF_EXCHANGE_LIST),  # Async DB insert
    #     service_exchange_list.setup_table_records(exchange_list),  # Async DB insert
    #     service_instrument_list.setup_table_records(instrument_list),  # Async DB insert
    positions = await asyncio.to_thread(get_kite_conn().positions)
    await service_positions.process_records(positions)
    holdings = await asyncio.to_thread(get_kite_conn().holdings)
    await service_holdings.process_records(holdings)
    # )
    await service_schedule_time.setup_table_records(DEF_SCHEDULE_TIME, skip_update_if_exists=True)
    await service_watch_list_instruments.setup_table_records(DEF_WATCH_LIST_INSTRUMENTS, skip_update_if_exists=True)


    # await asyncio.to_thread(ReportDownloader.login_download_reports)  # Run in a separate thread
    #
    # await ReportUploader.upload_reports()  # Async upload


if __name__ == "__main__":
    asyncio.run(run())  # Proper way to call an async function
