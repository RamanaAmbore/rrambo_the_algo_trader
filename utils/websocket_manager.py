import asyncio
from kiteconnect import KiteTicker
from market_cache import is_market_open, load_market_hours
from market_utils import get_active_instruments
from utils.db_conn import AsyncSessionLocal

API_KEY = "your_api_key"
ACCESS_TOKEN = "your_access_token"
kite_ws = KiteTicker(API_KEY, ACCESS_TOKEN)

async def subscribe_to_ticks():
    """Subscribe to live market data only if the market is open."""
    if not await is_market_open():
        print("Market closed, WebSocket not started.")
        return

    async with AsyncSessionLocal() as db_session:
        symbols = await get_active_instruments(db_session)
        tokens = [int(symbol) for symbol in symbols]
        if tokens:
            kite_ws.subscribe(tokens)
            kite_ws.set_mode(kite_ws.MODE_FULL, tokens)
            print(f"Subscribed to {len(tokens)} instruments.")

def on_ticks(ws, ticks):
    """Process tick data and update the database asynchronously."""
    print(f"Received ticks: {ticks}")
    asyncio.create_task(store_tick_data(ticks))

async def store_tick_data(ticks):
    """Store tick data only for active instruments in the database."""
    async with AsyncSessionLocal() as db_session:
        for tick in ticks:
            await db_session.execute(
                "UPDATE market_data SET open_price=:o, high_price=:h, low_price=:l, close_price=:c, volume=:v WHERE instrument_token=:t",
                {
                    "o": tick["ohlc"]["open"],
                    "h": tick["ohlc"]["high"],
                    "l": tick["ohlc"]["low"],
                    "c": tick["ohlc"]["close"],
                    "v": tick["volume"],
                    "t": tick["instrument_token"],
                },
            )
        await db_session.commit()

def on_connect(ws, response):
    """Handle WebSocket connection."""
    asyncio.run(subscribe_to_ticks())

def start_websocket():
    """Start the WebSocket only during market hours."""
    kite_ws.on_ticks = on_ticks
    kite_ws.on_connect = on_connect
    kite_ws.connect(threaded=True)
