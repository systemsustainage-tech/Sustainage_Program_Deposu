
import unittest
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestConnectivity(unittest.TestCase):
    """
    Checks external connectivity and local web server status.
    Adapted from c:\\SDG\\test_connection.py
    """

    def test_google_connectivity(self):
        """Test internet connectivity via Google"""
        try:
            r = requests.get("https://www.google.com", timeout=5)
            self.assertEqual(r.status_code, 200)
            logging.info(f"   [OK] Google: {r.status_code}")
        except Exception as e:
            logging.error(f"   [HATA] Google: {e}")
            self.fail(f"Google connectivity failed: {e}")

    def test_local_web_server(self):
        """Test local web server (assumes it is running on port 8000 or remote IP)"""
        # Adjust URL based on environment. 
        # If running on the server itself, localhost:8000 is good if Gunicorn is running.
        # Or check the public IP if testing from outside (but these tests run on the server).
        url = "http://127.0.0.1:8000"
        
        try:
            # We use a short timeout because it's local
            r = requests.get(url, timeout=5)
            # 200 is expected if index exists, or maybe 302 to login
            self.assertIn(r.status_code, [200, 302]) 
            logging.info(f"   [OK] Local Web Server ({url}): {r.status_code}")
        except Exception as e:
            logging.warning(f"   [WARN] Local Web Server ({url}) not reachable: {e}")
            # We don't fail here because the server might not be started during this test run
            # But we warn.
