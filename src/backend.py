# You should run the async function inside an event loop (e.g., in an async main function)

from src.app_initializer import app_initializer
from src.helpers.logger import get_logger

logger = get_logger(__name__)

import asyncio
import threading


async def backend_process():
    await app_initializer.setup()  # This starts the MarketTicker thread

    # Wait until MarketTicker (or any non-main thread) is done
    main_thread = threading.current_thread()
    while any(t.is_alive() for t in threading.enumerate() if t is not main_thread):
        await asyncio.sleep(1)  # Yield control, avoid busy-waiting


if __name__ == "__main__":
    asyncio.run(backend_process())
