
import unittest
import os
import sys
import sqlite3
import json
import time
from datetime import datetime, timedelta

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import web_app
from web_app import app, license_manager
from backend.yonetim.license_manager import LicenseManager

TEST_DB = 'test_tenant_api.db'

class TestTenantAPIKey(unittest.TestCase):
    def setUp(self):
        # Setup Test DB
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
            
        self.conn = sqlite3.connect(TEST_DB)
        self.cursor = self.conn.cursor()
        
        # Create necessary tables
        self.cursor.execute("""
            CREATE TABLE companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                license_key TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                max_users INTEGER DEFAULT 5,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        self.cursor.execute("INSERT INTO companies (name) VALUES ('Test Corp')")
        self.company_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Patch web_app to use test DB
        app.config['TESTING'] = True
        license_manager.db_path = TEST_DB
        self.client = app.test_client()
        
        # Create a valid license key using the actual LicenseManager logic
        self.lm = LicenseManager(TEST_DB)
        res = self.lm.generate_license(self.company_id, duration_days=30)
        self.valid_key = res['license_key']
        
    def tearDown(self):
        self.conn.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_missing_key(self):
        """Test API access without any key."""
        # Use a dummy API endpoint that requires license
        # We'll assume /api/v1/translations is protected or add a dummy route
        # web_app.py: license_check protects /api/ except login/register
        # Let's try to access /api/v1/translations (which is exempt? No, exempt list is ['api_login', 'api_register', 'api_logout', 'static'])
        # Wait, check web_app.py exempt list.
        # Line 339: if request.endpoint in ['api_login', 'api_register', 'api_logout', 'static']:
        # api_translations is defined at line 508. Its endpoint name is 'api_translations'.
        # So /api/v1/translations should be PROTECTED.
        
        response = self.client.get('/api/v1/translations')
        self.assertEqual(response.status_code, 403)
        self.assertIn('License verification failed', response.get_json().get('error'))

    def test_valid_key_header(self):
        """Test API access with valid X-License-Key header."""
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': self.valid_key})
        if response.status_code != 200:
            print(f"Failed with: {response.get_json()}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_key(self):
        """Test API access with invalid key."""
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': 'invalid_key_123'})
        self.assertEqual(response.status_code, 403)
        self.assertIn('Invalid license key', response.get_json().get('error'))

    def test_revoked_key(self):
        """Test API access with revoked key."""
        # Revoke the key
        self.cursor.execute("UPDATE licenses SET status='revoked' WHERE license_key=?", (self.valid_key,))
        self.conn.commit()
        
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': self.valid_key})
        self.assertEqual(response.status_code, 403)
        self.assertIn('License is revoked', response.get_json().get('error'))

    def test_expired_key(self):
        """Test API access with expired key."""
        # Generate expired key
        res = self.lm.generate_license(self.company_id, duration_days=-1) # Expired yesterday
        expired_key = res['license_key']
        
        response = self.client.get('/api/v1/translations', headers={'X-License-Key': expired_key})
        self.assertEqual(response.status_code, 403)
        self.assertIn('License has expired', response.get_json().get('error'))

if __name__ == '__main__':
    unittest.main()
