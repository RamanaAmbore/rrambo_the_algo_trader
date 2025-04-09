from src.managers.websocket_manager import WebSocketManager
from kiteconnect import KiteConnect
from bidict import bidict

api_key = "your_kite_api_key"
access_token = "your_kite_access_token"
memory_store = bidict()  # token ↔ symbol mapping, filled as needed

if __name__ == "__main__":
    ticker = WebSocketManager()
    ticker.start()
