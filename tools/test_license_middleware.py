import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, session, g
from remote_web_app import app, require_company_context, license_manager

class TestLicenseMiddleware(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Use existing route /api/saas/demo which is decorated with @require_company_context

    def tearDown(self):
        self.ctx.pop()

    @patch('remote_web_app.license_manager.get_active_license')
    @patch('remote_web_app.license_manager.verify_license_key')
    def test_valid_license(self, mock_verify, mock_get_license):
        # Setup mocks for a valid license
        mock_get_license.return_value = "valid_key"
        mock_verify.return_value = (True, "Valid", {'allowed_ips': None, 'allowed_domains': None})
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'test'}
            sess['company_id'] = 1
            
        response = self.client.get('/api/saas/demo')
        self.assertEqual(response.status_code, 200)
        # Check if response is JSON
        self.assertTrue(response.is_json)

    @patch('remote_web_app.license_manager.get_active_license')
    @patch('remote_web_app.license_manager.verify_license_key')
    @patch('remote_web_app.get_remote_address')
    def test_ip_restriction_block(self, mock_get_ip, mock_verify, mock_get_license):
        # Setup mocks for IP restriction
        mock_get_license.return_value = "restricted_key"
        # Allowed IP is 1.2.3.4, but client is 5.6.7.8
        mock_verify.return_value = (True, "Valid", {'allowed_ips': ['1.2.3.4'], 'allowed_domains': None})
        mock_get_ip.return_value = '5.6.7.8'
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'test'}
            sess['company_id'] = 1
            
        response = self.client.get('/api/saas/demo')
        # Expect 403 for API
        self.assertEqual(response.status_code, 403)
        self.assertIn("not authorized by license", response.get_json()['error'])

    @patch('remote_web_app.license_manager.get_active_license')
    @patch('remote_web_app.license_manager.verify_license_key')
    @patch('remote_web_app.get_remote_address')
    def test_ip_restriction_allow(self, mock_get_ip, mock_verify, mock_get_license):
        # Setup mocks for IP restriction
        mock_get_license.return_value = "restricted_key"
        # Allowed IP includes 5.6.7.8
        mock_verify.return_value = (True, "Valid", {'allowed_ips': ['1.2.3.4', '5.6.7.8'], 'allowed_domains': None})
        mock_get_ip.return_value = '5.6.7.8'
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'test'}
            sess['company_id'] = 1
            
        response = self.client.get('/api/saas/demo')
        self.assertEqual(response.status_code, 200)

    @patch('remote_web_app.license_manager.get_active_license')
    @patch('remote_web_app.license_manager.verify_license_key')
    def test_no_company_context(self, mock_verify, mock_get_license):
        # No company_id in session
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'test'}
            # sess['company_id'] missing
            
        response = self.client.get('/api/saas/demo')
        # Should redirect to login or clear session (current implementation redirects)
        self.assertEqual(response.status_code, 302) 

if __name__ == '__main__':
    unittest.main()
