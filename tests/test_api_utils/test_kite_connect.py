import unittest
from unittest.mock import patch, MagicMock
from models.access_token import AccessTokenHelper


class TestAccessTokenHelper(unittest.TestCase):
    def setUp(self):
        """Initialize AccessTokenHelper before each test."""
        self.token_helper = AccessTokenHelper()

    @patch("models.access_token.AccessTokenHelper.get_stored_access_token")
    def test_get_stored_access_token(self, mock_get_stored_access_token):
        """Test retrieving a stored access token."""
        mock_get_stored_access_token.return_value = "mocked_access_token"
        access_token = self.token_helper.get_stored_access_token()
        self.assertEqual(access_token, "mocked_access_token")
        mock_get_stored_access_token.assert_called_once()

    @patch("models.access_token.AccessTokenHelper.check_update_access_token")
    def test_check_update_access_token(self, mock_check_update_access_token):
        """Test updating the access token."""
        mock_check_update_access_token.return_value = True
        result = self.token_helper.check_update_access_token("new_mocked_token")
        self.assertTrue(result)
        mock_check_update_access_token.assert_called_once_with("new_mocked_token")

    @patch("models.access_token.AccessTokenHelper.get_stored_access_token")
    @patch("models.access_token.AccessTokenHelper.check_update_access_token")
    def test_access_token_workflow(self, mock_check_update_access_token, mock_get_stored_access_token):
        """Test full workflow of getting and updating the token."""
        mock_get_stored_access_token.return_value = None
        mock_check_update_access_token.return_value = True

        stored_token = self.token_helper.get_stored_access_token()
        self.assertIsNone(stored_token)

        update_result = self.token_helper.check_update_access_token("valid_new_token")
        self.assertTrue(update_result)

        mock_get_stored_access_token.assert_called_once()
        mock_check_update_access_token.assert_called_once_with("valid_new_token")


if __name__ == "__main__":
    unittest.main()
