import pytest
from unittest.mock import patch, MagicMock
from kiteconnect import TokenException
from kite_conn import ZerodhaKite
from kite_socket import ZerodhaSocket


@pytest.fixture(scope="function", autouse=True)
def mock_kite_connection():
    """Mock ZerodhaKite methods to prevent real API calls."""
    with patch.object(ZerodhaKite, "get_kite_connection") as mock_conn, \
         patch.object(ZerodhaKite, "_access_token", "mock_access_token"):
        mock_conn.return_value = MagicMock()
        yield


@pytest.fixture(scope="function", autouse=True)
def mock_market_monitor():
    """Mock MarketMonitor to control market open/close behavior."""
    with patch("kite_socket.MarketMonitor") as mock_monitor:
        monitor_instance = mock_monitor.return_value
        monitor_instance.is_market_open.return_value = True  # Default: Market is open
        yield monitor_instance


@pytest.fixture(scope="function")
def mock_socket_conn():
    """Mock WebSocket connection."""
    with patch("kiteconnect.KiteTicker") as mock_ticker:
        socket_instance = mock_ticker.return_value
        yield socket_instance


def test_setup_socket_conn_market_open(mock_socket_conn, mock_market_monitor):
    """Test WebSocket starts when the market is open."""
    ZerodhaSocket.get_socket_conn()
    mock_socket_conn.connect.assert_called_once()


def test_setup_socket_conn_market_closed(mock_socket_conn, mock_market_monitor):
    """Test WebSocket does not start when market is closed."""
    mock_market_monitor.is_market_open.return_value = False
    ZerodhaSocket.get_socket_conn()
    mock_socket_conn.connect.assert_not_called()


def test_on_close_token_exception(mock_socket_conn):
    """Test handling of TokenException when WebSocket closes."""
    with patch.object(ZerodhaSocket, "get_socket_conn") as mock_reconnect:
        ZerodhaSocket.on_close(mock_socket_conn, 1000, "TokenException: Invalid token")
        ZerodhaKite.get_kite_conn.assert_called_once()
        mock_reconnect.assert_called_once()


def test_on_close_reconnect(mock_socket_conn):
    """Test WebSocket reconnects on normal closure."""
    with patch.object(ZerodhaSocket, "get_socket_conn") as mock_reconnect:
        ZerodhaSocket.on_close(mock_socket_conn, 1000, "Normal closure")
        mock_reconnect.assert_called_once()


def test_add_instruments(mock_socket_conn):
    """Test adding instruments to WebSocket subscription."""
    ZerodhaSocket.add_instruments([12345, 67890])
    assert 12345 in ZerodhaSocket.instrument_tokens
    assert 67890 in ZerodhaSocket.instrument_tokens
    mock_socket_conn.subscribe.assert_called_once_with([12345, 67890])


def test_remove_instruments(mock_socket_conn):
    """Test removing instruments from WebSocket subscription."""
    ZerodhaSocket.instrument_tokens = {12345, 67890}
    ZerodhaSocket.remove_instruments([67890])
    assert 67890 not in ZerodhaSocket.instrument_tokens
    mock_socket_conn.unsubscribe.assert_called_once_with([67890])


if __name__ == "__main__":
    pytest.main()
