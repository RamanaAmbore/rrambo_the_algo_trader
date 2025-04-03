# You should run the async function inside an event loop (e.g., in an async main function)
import asyncio

from src.core.app_initializer import setup_parameters, get_kite_conn
from src.services.service_access_tokens import service_access_tokens
from src.services.service_schedule_list import service_schedule_list
from src.services.service_thread_list import service_thread_list
from src.services.service_watch_list import service_watch_list
from src.settings.constants_manager import DEF_WATCHLISTS, DEF_ACCESS_TOKENS, \
    DEF_THREAD_LIST, DEF_SCHEDULES


async def run():
    """Main execution function, running all tasks in parallel."""

    await setup_parameters()
    get_kite_conn()


    await asyncio.gather(
        service_access_tokens.setup_table_records(DEF_ACCESS_TOKENS, skip_update_if_exists=True),
        service_thread_list.setup_table_records(DEF_THREAD_LIST, skip_update_if_exists=True),
        service_schedule_list.setup_table_records(DEF_SCHEDULES, skip_update_if_exists=True),
        # service_watch_list.setup_table_records(DEF_WATCHLISTS, skip_update_if_exists=True),
    )


if __name__ == "__main__":
    asyncio.run(run())  # Proper way to call an async function
