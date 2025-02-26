import asyncio
from market_cache import load_market_hours, is_market_open
from websocket_manager import start_websocket

async def monitor_market_hours():
    """Refresh market hours cache and start WebSocket if needed."""
    await load_market_hours()  # Load market hours at startup
    while True:
        if await is_market_open():
            print("Market is open, starting WebSocket.")
            start_websocket()
            return  # Exit loop once WebSocket starts
        print("Market closed, checking again in 1 minute...")
        await asyncio.sleep(60)  # Avoid excessive checks

if __name__ == "__main__":
    asyncio.run(monitor_market_hours())
