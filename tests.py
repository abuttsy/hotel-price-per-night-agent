import unittest
from datetime import datetime
from scraper import HotelScraper
from email_manager import EmailManager
from unittest.mock import MagicMock, patch

class TestAutomation(unittest.TestCase):
    def test_regional_date_logic(self):
        scraper = HotelScraper()

        # Current year for the test
        year = datetime.now().year

        # Mocking datetime.now() to control test behavior
        with patch('scraper.datetime') as mock_datetime:
            # Set fixed current date: Oct 1, 2024
            mock_datetime.now.return_value = datetime(2024, 10, 1)
            mock_datetime.strptime = datetime.strptime

            # Test Europe
            dates = scraper.get_search_dates("Europe")
            self.assertEqual(dates, ("2024-11-10", "2024-11-17"))

            # Test Caribbean/Mexico (should be 2025 since Sep 2024 passed)
            dates = scraper.get_search_dates("Caribbean/Mexico")
            self.assertEqual(dates, ("2025-09-15", "2025-09-22"))

            # Test Default
            dates = scraper.get_search_dates("Unknown")
            self.assertEqual(dates, ("2024-11-10", "2024-11-17"))

    def test_price_swing_alert_logic(self):
        # We'll mock the internal _send_email to see if it's called
        email_mgr = EmailManager("sender@test.com", "pass", "receiver@test.com")
        email_mgr._send_email = MagicMock()

        # Test 20% increase
        email_mgr.send_price_alert("Test Hotel", 100, 120)
        email_mgr._send_email.assert_called()
        email_mgr._send_email.reset_mock()

        # Test 20% decrease
        email_mgr.send_price_alert("Test Hotel", 100, 80)
        email_mgr._send_email.assert_called()
        email_mgr._send_email.reset_mock()

        # Test 10% increase (should NOT send)
        email_mgr.send_price_alert("Test Hotel", 100, 110)
        email_mgr._send_email.assert_not_called()

        # Test None old price (should NOT send)
        email_mgr.send_price_alert("Test Hotel", None, 120)
        email_mgr._send_email.assert_not_called()

if __name__ == "__main__":
    unittest.main()
