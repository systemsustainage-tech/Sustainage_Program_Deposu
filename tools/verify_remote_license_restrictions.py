
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, request, jsonify, g, session

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing remote_web_app
mock_limiter = MagicMock()
def limit_decorator(*args, **kwargs):
    def decorator(f):
        return f
    return decorator
mock_limiter.limit.side_effect = limit_decorator
mock_limiter.exempt = lambda f: f

# Mock prometheus_flask_exporter
mock_prometheus = MagicMock()
sys.modules['prometheus_flask_exporter'] = mock_prometheus

# Mock psutil and flask_limiter
with patch('psutil.cpu_percent', return_value=10), \
     patch('psutil.virtual_memory', return_value=MagicMock(percent=20)), \
     patch('flask_limiter.Limiter', return_value=mock_limiter):
    try:
        # IMPORT remote_web_app INSTEAD OF web_app
        from remote_web_app import app, license_manager
    except ImportError:
        # Fallback if imports fail
        print("Import failed, attempting to mock modules...")
        sys.modules['security.core.secure_password'] = MagicMock()
        sys.modules['security.core.enhanced_2fa'] = MagicMock()
        from remote_web_app import app, license_manager

class TestLicenseRestrictions(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Mock LicenseManager methods
        self.original_verify = license_manager.verify_license_key
        self.original_get_active = license_manager.get_active_license
        
        license_manager.verify_license_key = MagicMock()
        license_manager.get_active_license = MagicMock()
        
    def tearDown(self):
        self.app_context.pop()
        license_manager.verify_license_key = self.original_verify
        license_manager.get_active_license = self.original_get_active

    def test_ip_restriction_allowed(self):
        # Setup: Valid license, allowed IP
        payload = {'allowed_ips': ['127.0.0.1'], 'company_id': 1}
        # In remote_web_app, get_active_license is called first
        license_manager.get_active_license.return_value = 'valid_key'
        license_manager.verify_license_key.return_value = (True, "Valid", payload)
        
        # Mock session to satisfy require_company_context
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'role': 'Admin'}
            sess['company_id'] = 1

        # Action: Request from allowed IP
        # Note: saas_demo_api uses @require_company_context
        response = self.client.get('/api/saas/demo', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        
        # Assert
        self.assertNotEqual(response.status_code, 403, f"Should be allowed. Response: {response.json if response.is_json else response.data}")

    def test_ip_restriction_denied(self):
        # Setup: Valid license, allowed IP is DIFFERENT
        payload = {'allowed_ips': ['10.0.0.1'], 'company_id': 1}
        license_manager.get_active_license.return_value = 'valid_key'
        license_manager.verify_license_key.return_value = (True, "Valid", payload)
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'role': 'Admin'}
            sess['company_id'] = 1

        # Action: Request from 127.0.0.1
        response = self.client.get('/api/saas/demo', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertIn("not authorized by license", str(response.json.get('error', '')) or str(response.data))

    def test_domain_restriction_allowed(self):
        # Setup
        payload = {'allowed_domains': ['localhost'], 'company_id': 1}
        license_manager.get_active_license.return_value = 'valid_key'
        license_manager.verify_license_key.return_value = (True, "Valid", payload)
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'role': 'Admin'}
            sess['company_id'] = 1

        # Action
        response = self.client.get('/api/saas/demo', environ_base={'HTTP_HOST': 'localhost:5000'})
        
        # Assert
        self.assertNotEqual(response.status_code, 403)

    def test_domain_restriction_denied(self):
        # Setup
        payload = {'allowed_domains': ['example.com'], 'company_id': 1}
        license_manager.get_active_license.return_value = 'valid_key'
        license_manager.verify_license_key.return_value = (True, "Valid", payload)
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'role': 'Admin'}
            sess['company_id'] = 1

        # Action
        response = self.client.get('/api/saas/demo', environ_base={'HTTP_HOST': 'localhost:5000'})
        
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertIn("not authorized by license", str(response.json.get('error', '')) or str(response.data))

if __name__ == "__main__":
    unittest.main()
