# You should run the async function inside an event loop (e.g., in an async main function)

import asyncio

from src.app_initializer import app_initializer
from src.app_state import app_state
from src.helpers.logger import get_logger
from src.services.service_holdings import service_holdings
from src.services.service_instrument_list import service_instrument_list
from src.services.service_positions import service_positions
from src.services.service_schedule_time import service_schedule_time
from src.services.service_watch_list_instruments import service_watch_list_instruments

logger = get_logger(__name__)

async def backend_process():
    await app_initializer.setup_parameters()

    positions = await asyncio.to_thread(app_initializer.get_kite_conn().positions)
    await service_positions.process_records(positions)
    app_state.positions = await service_positions.get_records_map()
    symbol_map1 = await service_holdings.get_records_map()
    symbol_map2 = await service_instrument_list.get_records_map()
    symbol_map3 = await service_watch_list_instruments.get_records_map()

if __name__ == "__main__":
    asyncio.run(backend_process())  # Proper way to call an async function