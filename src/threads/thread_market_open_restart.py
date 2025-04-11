# You should run the async function inside an event loop (e.g., in an async main function)

import asyncio

from src.core.app_initializer import app_initializer
from src.helpers.logger import get_logger
from src.services.service_holdings import service_holdings
from src.services.service_instrument_list import service_instrument_list
from src.services.service_positions import service_positions
from src.services.service_watch_list_instruments import service_watch_list_instruments

logger = get_logger(__name__)

async def market_open_restart():
    await app_initializer.setup_parameters()
    positions = await asyncio.to_thread(app_initializer.get_kite_conn().positions)
    await service_positions.process_records(positions)
    symbol_map = await service_positions.get_symbol_map()
    symbol_map1 = await service_holdings.get_symbol_map()
    symbol_map2 = await service_instrument_list.get_symbol_map()
    symbol_map3 = await service_watch_list_instruments.get_symbol_map()

if __name__ == "__main__":
    asyncio.run(market_open_restart())  # Proper way to call an async function