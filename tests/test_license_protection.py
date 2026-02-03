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
from backend.yonetim.license_manager import LicenseManager

class TestLicenseProtection(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = self.db_path
        self.client = self.app.test_client()
        
        # Initialize DB
        self._init_db()
        
        # Mock LicenseManager methods used in web_app
        self.license_manager_mock = MagicMock()
        # Patch the global license_manager instance in web_app
        self.patcher = patch('web_app.license_manager', self.license_manager_mock)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create minimal users table for session login simulation
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                password_hash TEXT,
                role TEXT,
                company_id INTEGER,
                is_active INTEGER DEFAULT 1,
                failed_attempts INTEGER DEFAULT 0,
                locked_until REAL
            )
        """)
        
        # Create licenses table
        cursor.execute("""
            CREATE TABLE licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                license_key TEXT,
                issued_at TIMESTAMP,
                expires_at TIMESTAMP,
                max_users INTEGER,
                status TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        conn.commit()
        conn.close()

    def test_access_without_license(self):
        """Test accessing a protected API endpoint without any license info."""
        # Use an existing route that falls under license check
        response = self.client.get('/api/v1/dashboard-stats')
        
        # Should be 403 Forbidden because no header and no session
        self.assertEqual(response.status_code, 403)
        self.assertIn('License verification failed', response.get_json().get('error', ''))

    def test_access_with_invalid_header_license(self):
        """Test accessing with an invalid X-License-Key."""
        self.license_manager_mock.verify_license_key.return_value = (False, "Invalid Key", None)
        
        response = self.client.get('/api/v1/dashboard-stats', headers={'X-License-Key': 'invalid-key'})
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('License Error', response.get_json().get('error', ''))
        self.license_manager_mock.verify_license_key.assert_called_with('invalid-key')

    def test_access_with_valid_header_license(self):
        """Test accessing with a valid X-License-Key."""
        self.license_manager_mock.verify_license_key.return_value = (True, "Valid", {"company_id": 1})
        
        response = self.client.get('/api/v1/dashboard-stats', headers={'X-License-Key': 'valid-key'})
        
        # If license check passes, it might fail later due to DB/Auth, but NOT 403 License Error
        if response.status_code == 403:
            # Only fail if it's a license error
            error_msg = response.get_json().get('error', '')
            self.assertNotIn('License', error_msg)
        
        self.license_manager_mock.verify_license_key.assert_called_with('valid-key')

    def test_access_with_session_no_active_license(self):
        """Test logged in user but company has no active license."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['company_id'] = 1
            
        self.license_manager_mock.get_active_license.return_value = None
        
        response = self.client.get('/api/v1/dashboard-stats')
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('No active license found', response.get_json().get('error', ''))
        self.license_manager_mock.get_active_license.assert_called_with(1)

    def test_access_with_session_valid_license(self):
        """Test logged in user with valid active license."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['company_id'] = 1
            
        self.license_manager_mock.get_active_license.return_value = 'valid-db-key'
        self.license_manager_mock.verify_license_key.return_value = (True, "Valid", {"company_id": 1})
        
        response = self.client.get('/api/v1/dashboard-stats')
        
        # If license check passes, it might fail later due to DB/Auth, but NOT 403 License Error
        if response.status_code == 403:
            error_msg = response.get_json().get('error', '')
            self.assertNotIn('License', error_msg)
            
        self.license_manager_mock.get_active_license.assert_called_with(1)
        self.license_manager_mock.verify_license_key.assert_called_with('valid-db-key')

if __name__ == '__main__':
    from flask import jsonify
    unittest.main()
