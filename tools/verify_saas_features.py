import unittest
import json
import sqlite3
import os
import sys

# Add root to path to import remote_web_app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from remote_web_app import app, DB_PATH, get_db

class SaasVerificationTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_secret'
        self.client = self.app.test_client()
        
        # Ensure test user exists
        self.create_test_user()
        
    def create_test_user(self):
        conn = sqlite3.connect(DB_PATH)
        # Check if company 999 exists
        conn.execute("INSERT OR IGNORE INTO companies (id, name) VALUES (999, 'Test Company')")
        # Check if user 'saas_test' exists
        # Use simple hashing for test or just rely on existing login logic if possible
        # But remote_web_app uses Argon2 or Werkzeug. 
        # For simplicity, we will simulate a session directly in tests or create a user that bypasses complex auth if needed.
        # But better: Use the 'admin_test' session logic in login route?
        # The login route has a hardcoded 'admin' check: 
        # "exists = conn.execute("SELECT 1 FROM users WHERE username='admin'").fetchone()"
        # If admin exists, it allows login as 'admin_test' if password fails? No, wait.
        
        # Let's look at login logic in remote_web_app.py:
        # if verify_password(password, user['password_hash']): ...
        
        # To avoid password hashing complexity in test setup, 
        # I will use `with client.session_transaction() as sess:` to set the session directly!
        conn.commit() # Important!
        conn.close()

    def test_unauthorized_access(self):
        """Test accessing dashboard without login redirects to login"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])
        
        response = self.client.get('/api/saas/demo')
        self.assertEqual(response.status_code, 401) # API should return 401

    def test_authorized_access_dashboard(self):
        """Test accessing dashboard with valid session"""
        with self.client.session_transaction() as sess:
            sess['user'] = 'saas_test_user'
            sess['user_id'] = 123
            sess['company_id'] = 999 # Use our test company
            sess['role'] = 'admin'

        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Company', response.data) # Assuming company name is shown, or just 200 OK

    def test_saas_demo_api(self):
        """Test SaaS Demo API returns correct company context"""
        with self.client.session_transaction() as sess:
            sess['user'] = 'saas_test_user'
            sess['company_id'] = 999 

        response = self.client.get('/api/saas/demo')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['company_id'], 999)
        self.assertEqual(data['tenant_status'], 'active')
        self.assertEqual(data['company_name'], 'Test Company')

    def test_dashboard_stats_api(self):
        """Test Dashboard Stats API"""
        with self.client.session_transaction() as sess:
            sess['user'] = 'saas_test_user'
            sess['company_id'] = 999 

        response = self.client.get('/api/dashboard/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should contain keys
        self.assertIn('energy_consumption', data)
        self.assertIn('water_consumption', data)
        self.assertIn('waste_amount', data)

if __name__ == '__main__':
    unittest.main()
