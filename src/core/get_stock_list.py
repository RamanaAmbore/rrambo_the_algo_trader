from src.services.service_access_token import save_stock_list
from src.core.database_manager import DatabaseManager as Db
from src.helpers.logger import get_logger

logger = get_logger(__name__)


def fetch_kite_stock_list():
    """
    Fetches the list of stocks from Zerodha Kite API.
    Returns a list of dictionaries containing tradingsymbol, name, yahoo_ticker, and exchange.
    """
    kite = Db.get_sync_session()
    instruments = kite.instruments("NSE")
    stock_list = []

    for instrument in instruments:
        tradingsymbol = instrument["tradingsymbol"]
        name = instrument.get("name", tradingsymbol)
        yahoo_ticker = f"{tradingsymbol}.NS"
        exchange = instrument["exchange"]

        stock_list.append({
            "tradingsymbol": tradingsymbol,
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