import asyncio

from src.app_state_manager import AppState
from src.core.singleton_base import SingletonBase
from src.models.websocket_tick import WebsocketTick
from src.services.service_base import ServiceBase


# your db session


class ServiceWebsocketTick(SingletonBase, ServiceBase):

    def __init__(self, memory_store):
        self.queue = asyncio.Queue()
        self.market_state = AppState()

    async def enqueue_tick(self, tick: dict):
        await self.queue.put(tick)

    async def process_ticks(self):
        while True:
            tick = await self.queue.get()
            try:
                await self.save_to_db(tick)
            except Exception as e:
                print(f"Error saving tick: {e}")

    async def save_to_db(self, tick: dict):
        async with get_async_session() as session:
            model = self._map_to_model(tick)
            session.add(model)
            await session.commit()

    def _map_to_model(self, tick: dict) -> WebsocketTick:
        return WebsocketTick(
            instrument_token=tick.get("instrument_token"),
            last_price=tick.get("last_price"),
            last_traded_quantity=tick.get("last_traded_quantity"),
            average_price=tick.get("average_price"),
            volume_traded=tick.get("volume_traded"),
            total_buy_quantity=tick.get("total_buy_quantity"),
            total_sell_quantity=tick.get("total_sell_quantity"),
            ohlc_open=tick.get("ohlc", {}).get("open"),
            ohlc_high=tick.get("ohlc", {}).get("high"),
            ohlc_low=tick.get("ohlc", {}).get("low"),
            ohlc_close=tick.get("ohlc", {}).get("close"),
            change=tick.get("change"),
            last_trade_time=tick.get("last_trade_time"),
            exchange_timestamp=tick.get("exchange_timestamp"),
            oi=tick.get("oi"),
            oi_day_high=tick.get("oi_day_high"),
            oi_day_low=tick.get("oi_day_low"),
            depth=str(tick.get("depth")),
            tradable=tick.get("tradable"),
            mode=tick.get("mode"),
        )
