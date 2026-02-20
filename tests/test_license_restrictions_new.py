import unittest
import json
import sqlite3
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock missing dependencies BEFORE importing web_app
import tests.mocks_for_missing_deps

from web_app import app

class TestLicenseRestrictions(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = self.db_path
        self.client = self.app.test_client()
        
        # Mock LicenseManager methods used in web_app
        self.license_manager_mock = MagicMock()
        # Patch the global license_manager instance in web_app
        self.patcher = patch('web_app.license_manager', self.license_manager_mock)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_allowed_domain_success(self):
        """Test access with valid allowed_domains."""
        # Mock payload with allowed domain (localhost is default in test_client)
        payload = {
            "company_id": 1, 
            "allowed_domains": ["localhost", "example.com"]
        }
        self.license_manager_mock.verify_license_key.return_value = (True, "Valid", payload)
        
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': 'valid-key'})
        # Should be 200 OK
        self.assertEqual(response.status_code, 200)

    def test_allowed_domain_failure(self):
        """Test access failure when domain is not in allowed list."""
        payload = {
            "company_id": 1, 
            "allowed_domains": ["example.com"]
        }
        self.license_manager_mock.verify_license_key.return_value = (True, "Valid", payload)
        
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': 'valid-key'})
        # Should be 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertIn("Domain 'localhost' not authorized", response.get_json().get('error', ''))

    def test_allowed_ip_success(self):
        """Test access with valid allowed_ips."""
        # Mock payload with allowed IP. Test client usually sends 127.0.0.1
        payload = {
            "company_id": 1, 
            "allowed_ips": ["127.0.0.1", "10.0.0.1"]
        }
        self.license_manager_mock.verify_license_key.return_value = (True, "Valid", payload)
        
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': 'valid-key'})
        self.assertEqual(response.status_code, 200)

    def test_allowed_ip_failure(self):
        """Test access failure when IP is not in allowed list."""
        payload = {
            "company_id": 1, 
            "allowed_ips": ["10.0.0.1"]
        }
        self.license_manager_mock.verify_license_key.return_value = (True, "Valid", payload)
        
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': 'valid-key'})
        self.assertEqual(response.status_code, 403)
        self.assertIn("IP '127.0.0.1' not authorized", response.get_json().get('error', ''))

if __name__ == '__main__':
    unittest.main()
