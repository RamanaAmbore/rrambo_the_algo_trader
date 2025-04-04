# You should run the async function inside an event loop (e.g., in an async main function)
import asyncio

from src.core.app_initializer import setup_parameters, get_kite_conn
from src.services.service_exchange_list import service_exchange_list
from src.services.service_schedule_time import service_schedule_time
from src.services.service_thread_schedule import service_thread_schedule
from src.services.service_schedule_list import service_schedule_list
from src.services.service_thread_list import service_thread_list
from src.settings.constants_manager import DEF_THREAD_LIST, DEF_SCHEDULES, DEF_THREAD_SCHEDULE, DEF_SCHEDULE_TIME, \
    DEF_EXCHANGE_LIST


async def run():
    """Main execution function, running all tasks in parallel."""

    await setup_parameters()

    await asyncio.gather(
        service_thread_list.setup_table_records(DEF_THREAD_LIST, skip_update_if_exists=True),
        service_schedule_list.setup_table_records(DEF_SCHEDULES, skip_update_if_exists=True),
        # service_watch_list.setup_table_records(DEF_WATCHLISTS, skip_update_if_exists=True),
    )

    await service_thread_schedule.setup_table_records(DEF_THREAD_SCHEDULE, skip_update_if_exists=True)

    records = await asyncio.to_thread(get_kite_conn().instruments)  # Run in a separate thread
    exchange_set = {record["exchange"] for record in records}
    exchange_set = [{'exchange': record} for record in exchange_set]
    await service_exchange_list.setup_table_records(DEF_EXCHANGE_LIST)  # Async DB insert
    await service_exchange_list.setup_table_records(exchange_set)  # Async DB insert


    # await service_schedule_time.setup_table_records(DEF_SCHEDULE_TIME, skip_update_if_exists=True),


if __name__ == "__main__":
    asyncio.run(run())  # Proper way to call an async function
