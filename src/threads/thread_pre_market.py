# You should run the async function inside an event loop (e.g., in an async main function)

import asyncio

from src.core.app_initializer import app_initializer
from src.core.decorators import track_exec_time
from src.helpers.logger import get_logger
from src.models import ScheduleTime

logger = get_logger(__name__)
model = ScheduleTime


@track_exec_time()
async def run():
    """Main execution function, running all tasks in parallel."""

    await app_initializer.setup_parameters()
    await app_initializer.setup_pre_market()

    # await sync_reports()


if __name__ == "__main__":
    asyncio.run(run())  # Proper way to call an async function
