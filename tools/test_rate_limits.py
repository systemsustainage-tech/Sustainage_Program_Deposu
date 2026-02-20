
import sys
import os
import unittest
import time
from unittest.mock import MagicMock, patch
from flask import Flask, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies that might be missing or require DB
sys.modules['modules.sdg.sdg_manager'] = MagicMock()
sys.modules['core.language_manager'] = MagicMock()
sys.modules['core.database'] = MagicMock()
sys.modules['yonetim.license_manager'] = MagicMock()
sys.modules['prometheus_flask_exporter'] = MagicMock()
# Mock psutil to return valid numbers
mock_psutil = MagicMock()
mock_psutil.cpu_percent.return_value = 10.0
mock_psutil.virtual_memory.return_value.percent = 20.0
sys.modules['psutil'] = mock_psutil

# We need the real remote_web_app but with some mocks
# Since remote_web_app imports a lot of stuff at top level, we might need more mocks
# Ideally we should have used dependency injection or factory pattern, but we work with what we have.

# Strategy: Mock ALL modules in 'modules' and 'core' that are not essential for routing/limiting
for mod in ['modules.environmental.carbon_manager', 'modules.environmental.carbon_reporting', 
            'modules.environmental.energy_manager', 'modules.environmental.energy_reporting',
            'modules.environmental.water_manager', 'modules.environmental.water_reporting',
            'modules.environmental.waste_manager', 'modules.environmental.waste_reporting',
            'modules.social.social_manager', 'modules.social.social_reporting',
            'modules.governance.corporate_governance', 'modules.governance.governance_reporting',
            'mapping.sdg_gri_mapping', 'modules.gri.gri_manager', 'modules.esg.esg_manager',
            'modules.cbam.cbam_manager', 'modules.csrd.csrd_compliance_manager',
            'modules.eu_taxonomy.taxonomy_manager', 'modules.environmental.biodiversity_manager',
            'modules.economic.economic_value_manager', 'modules.super_admin.components.rate_limiter']:
    sys.modules[mod] = MagicMock()

# Now import app
from remote_web_app import app, limiter

class TestRateLimits(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Configure license manager mock to avoid invalid return error
        import remote_web_app
        remote_web_app.license_manager.get_active_license.return_value = "test_license_key"
        # Must return tuple of 3: (is_valid, msg, payload)
        remote_web_app.license_manager.verify_license_key.return_value = (True, "Valid", {'allowed_ips': None, 'allowed_domains': None})
        
        # Reset limiter storage
        if hasattr(limiter, '_storage'):
            limiter._storage.reset()
            
    def tearDown(self):
        self.app_context.pop()

    def test_data_add_rate_limit(self):
        # Limit is 10 per minute
        # We need to be authenticated and have company context
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'test'}
            sess['company_id'] = 1
            sess['role'] = 'User'

        # Make 10 allowed requests
        for i in range(10):
            response = self.client.get('/data/add', environ_base={'REMOTE_ADDR': '127.0.0.1'})
            # We expect 200 or 302 (redirect) or maybe template rendering error if templates missing
            # But NOT 429
            self.assertNotEqual(response.status_code, 429, f"Request {i+1} failed with 429")

        # 11th request should fail
        response = self.client.get('/data/add', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assertEqual(response.status_code, 429, "Should be rate limited (429) after 10 requests")

    def test_report_add_rate_limit(self):
        # Limit is 5 per minute
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'username': 'test'}
            sess['company_id'] = 1
            sess['role'] = 'User'

        # Make 5 allowed requests
        for i in range(5):
            response = self.client.get('/reports/add', environ_base={'REMOTE_ADDR': '127.0.0.1'})
            self.assertNotEqual(response.status_code, 429, f"Request {i+1} failed with 429")

        # 6th request should fail
        response = self.client.get('/reports/add', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assertEqual(response.status_code, 429, "Should be rate limited (429) after 5 requests")

if __name__ == "__main__":
    unittest.main()
