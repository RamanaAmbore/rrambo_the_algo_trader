import pytest
from unittest.mock import patch, MagicMock
from kiteconnect import KiteConnect
from requests.exceptions import HTTPError
from zerodha_kite import ZerodhaKite


@pytest.fixture(scope="function", autouse=True)
def mock_environment():
    """Mock environment variables."""
    with patch("zerodha_kite.os.getenv") as mock_getenv:
        mock_getos.getenv("side_effect = lambda key: {
            "API_KEY": "mock_api_key",
            "API_SECRET": "mock_api_secret",
            "ZERODHA_USERNAME": "mock_user",
            "ZERODHA_PASSWORD": "mock_pass",
            "LOGIN_URL": "https://mocklogin.url",
            "TWOFA_URL": "https://mocktwofa.url",
            "TOTP_TOKEN": "mock_totp"
        }.get(key)
        yield


@pytest.fixture(scope="function", autouse=True)
def mock_db_access_token():
    """Mock AccessToken storage."""
    with patch("zerodha_kite.AccessToken") as mock_db:
        mock_db_instance = mock_db.return_value
        yield mock_db_instance


@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests session for login and two-factor authentication."""
    with patch("zerodha_kite.requests.Session") as mock_session:
        session_instance = mock_session.return_value
        session_instance.post.return_value.raise_for_status = MagicMock()
        session_instance.post.return_value.json.return_value = {"data": {"request_id": "mock_request_id"}}
        session_instance.get.return_value.text = "request_token=mock_request_token&"
        yield session_instance


@pytest.fixture(scope="function")
def mock_kiteconnect():
    """Mock KiteConnect API."""
    with patch.object(KiteConnect, "generate_session") as mock_generate_session:
        mock_kite = MagicMock()
        mock_generate_session.return_value = {"access_token": "mock_access_token"}
        yield mock_kite


def test_successful_authentication(mock_db_access_token, mock_requests, mock_kiteconnect):
    """Test successful authentication and access token retrieval."""
    mock_db_access_token.get_stored_access_token.return_value = None
    ZerodhaKite.get_kite_conn()
    assert ZerodhaKite._access_token == "mock_access_token"
    mock_db_access_token.check_update_access_token.assert_called_once_with("mock_access_token")


def test_stored_token_valid(mock_db_access_token):
    """Test using a valid stored token."""
    mock_db_access_token.get_stored_access_token.return_value = "stored_valid_token"

    with patch.object(KiteConnect, "profile", return_value={"user_id": "mock_user"}):
        ZerodhaKite.get_kite_conn()

    assert ZerodhaKite._access_token == "stored_valid_token"


def test_stored_token_invalid(mock_db_access_token):
    """Test handling of an invalid stored token."""
    mock_db_access_token.get_stored_access_token.return_value = "invalid_token"

    with patch.object(KiteConnect, "profile", side_effect=Exception("Invalid token")):
        with patch.object(ZerodhaKite, "_authenticate") as mock_authenticate:
            ZerodhaKite.get_kite_conn()
            mock_authenticate.assert_called_once()


def test_login_failure(mock_requests):
    """Test login failure handling."""
    mock_requests.post.side_effect = HTTPError("Login failed")

    with pytest.raises(HTTPError, match="Login failed"):
        ZerodhaKite.get_kite_conn()


def test_totp_failure(mock_requests):
    """Test failure in TOTP authentication."""
    mock_requests.post.side_effect = [MagicMock(), HTTPError("TOTP failed")]

    with pytest.raises(HTTPError, match="TOTP failed"):
        ZerodhaKite.get_kite_conn()


def test_access_token_generation_failure(mock_requests, mock_kiteconnect):
    """Test failure in access token generation."""
    mock_kiteconnect.generate_session.side_effect = Exception("Access token failure")

    with pytest.raises(Exception, match="Access token failure"):
        ZerodhaKite.get_kite_conn()


if __name__ == "__main__":
    pytest.main()
