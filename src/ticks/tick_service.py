from src.ticks.tick_model import TickModel
from src.ticks.tick_queue_manager import TickQueueManager
from src.core.singleton_base import SingletonBase


class TickService(SingletonBase):
    def __init__(self):
        self.queue_manager = TickQueueManager()

    def process_ticks(self, ticks):
        for tick in ticks:
            model = self._convert_to_model(tick)
            self.queue_manager.enqueue(model)

    @staticmethod
    def _convert_to_model(tick_data: dict) -> TickModel:
        ohlc = tick_data.get("ohlc", {})
        return TickModel(
            instrument_token=tick_data["instrument_token"],
            last_price=tick_data.get("last_price", 0.0),
            last_traded_quantity=tick_data.get("last_traded_quantity"),
            average_traded_price=tick_data.get("average_traded_price"),
            volume_traded=tick_data.get("volume_traded"),
            total_buy_quantity=tick_data.get("buy_quantity"),
            total_sell_quantity=tick_data.get("sell_quantity"),
            ohlc_open=ohlc.get("open"),
            ohlc_high=ohlc.get("high"),
            ohlc_low=ohlc.get("low"),
            ohlc_close=ohlc.get("close"),
            change=tick_data.get("change"),
            exchange_timestamp=tick_data.get("exchange_timestamp"),
            oi=tick_data.get("oi"),
            oi_day_high=tick_data.get("oi_day_high"),
            oi_day_low=tick_data.get("oi_day_low"),
        )
