import asyncio
import threading

from src.app_initializer import app_initializer
from src.helpers.logger import get_logger

logger = get_logger(__name__)


async def backend_process():
    await app_initializer.setup()  # This starts background threads (e.g. Ticker)

    # Keep the async loop alive until all non-main threads finish
    main_thread = threading.current_thread()
    while True:
        alive_threads = [t for t in threading.enumerate() if t is not main_thread and t.is_alive()]
        if not alive_threads:
            break
        await asyncio.sleep(5)  # Yield control and avoid CPU hogging


if __name__ == "__main__":
    asyncio.run(backend_process())

