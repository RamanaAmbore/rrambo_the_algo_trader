from models.access_token import save_stock_list
from utils.db_connection import DbConnection
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_kite_stock_list():
    """
    Fetches the list of stocks from Zerodha Kite API.
    Returns a list of dictionaries containing symbol, name, yahoo_ticker, and exchange.
    """
    kite = DbConnection.get_sync_session()
    instruments = kite.instruments("NSE")
    stock_list = []

    for instrument in instruments:
        symbol = instrument["tradingsymbol"]
        name = instrument.get("name", symbol)
        yahoo_ticker = f"{symbol}.NS"
        exchange = instrument["exchange"]

        stock_list.append({
            "symbol": symbol,
            "name": name,
            "yahoo_ticker": yahoo_ticker,
            "exchange": exchange
        })

    return stock_list


def update_stock_list_in_db():
    """
    Fetches the latest stock list and updates the database.
    """
    try:
        stock_list = fetch_kite_stock_list()
        if stock_list:
            save_stock_list(stock_list)
            print("Stock list updated successfully.")
        else:
            print("No stocks found to update.")
    except Exception as e:
        print(f"Error updating stock list: {e}")


if __name__ == "__main__":
    logger.info(f'Executing fetch_kite_stock_list()')
    fetch_kite_stock_list()