# You should run the async function inside an event loop (e.g., in an async main function)

import asyncio

from src.core.app_initializer import app_initializer
from src.helpers.logger import get_logger
from src.services.service_positions import service_positions

logger = get_logger(__name__)

async def market_open_restart():
    await app_initializer.setup_parameters()
    positions = await asyncio.to_thread(app_initializer.get_kite_conn().positions)
    service_positions.process_records(positions),

if __name__ == "__main__":
    asyncio.run(market_open_restart())  # Proper way to call an async function