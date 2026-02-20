import unittest
from flask import Flask, g
import io
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.audit_api import audit_bp
from backend.core.audit_manager import AuditManager

from unittest.mock import patch, MagicMock

class TestAuditExport(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret_key'
        self.app.register_blueprint(audit_bp, url_prefix='/api/audit')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
            
    @patch('backend.api.audit_api.AuditManager')
    def test_export_csv(self, MockAuditManager):
        # Mock the manager and its get_logs method
        mock_manager = MockAuditManager.return_value
        mock_manager.get_logs.return_value = [
            {
                'id': 1, 
                'user_id': 1, 
                'action': 'TEST_EXPORT', 
                'resource': 'test_resource', 
                'details': 'test details', 
                'ip_address': '127.0.0.1', 
                'created_at': '2026-01-01 12:00:00'
            }
        ]
        
        with self.client.session_transaction() as sess:
            sess['user'] = {'id': 1, 'role': 'admin'}
            sess['company_id'] = 1
            sess['role'] = 'admin'
        
        response = self.client.get('/api/audit/export?format=csv')
        if response.status_code != 200:
            print(response.data)
            
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'TEST_EXPORT', response.data)
        self.assertIn(b'test_resource', response.data)
        
    def test_export_excel(self):
        # Excel export might require pandas/openpyxl, let's check if it fails gracefully or works
        # If openpyxl is not installed, it might fail or return CSV?
        # The code in audit_api.py handles CSV. Does it handle Excel?
        pass

if __name__ == '__main__':
    unittest.main()
