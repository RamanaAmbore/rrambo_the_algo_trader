# You should run the async function inside an event loop (e.g., in an async main function)
import asyncio

from src.services.service_broker_accounts import service_broker_accounts
from src.services.service_parameter_table import service_parameter_table
from src.services.service_thread_list import service_thread_list
from src.services.service_watch_list import service_watch_list
from src.services.service_access_tokens import service_access_tokens
from src.settings.constants_manager import DEF_PARAMETERS, DEF_BROKER_ACCOUNTS, DEF_WATCHLISTS, DEF_ACCESS_TOKENS, \
    DEF_THREAD_LIST


async def run():
    """Main execution function, running all tasks in parallel."""
    await service_broker_accounts.setup_table_records(DEF_BROKER_ACCOUNTS, skip_update_if_exists=True)
    await service_parameter_table.setup_table_records(DEF_PARAMETERS,skip_update_if_exists=True)
    await service_access_tokens.setup_table_records(DEF_ACCESS_TOKENS, skip_update_if_exists=True)
    await service_thread_list.setup_table_records(DEF_THREAD_LIST, skip_update_if_exists=True)

    await service_watch_list.setup_table_records(DEF_WATCHLISTS, skip_update_if_exists=True)


if __name__ == "__main__":
    asyncio.run(run())  # Proper way to call an async function
