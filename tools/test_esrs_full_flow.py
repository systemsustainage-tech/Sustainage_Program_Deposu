
import sys
import os
import unittest
import logging
from flask import Flask, session

# Add paths
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

from backend.modules.esrs.esrs_manager import ESRSManager
from web_app import app

# Setup logging
logging.basicConfig(level=logging.INFO)

class TestESRSFlow(unittest.TestCase):
    def setUp(self):
        # Use absolute path for test db
        self.db_path = os.path.join(os.getcwd(), 'test_esrs.sqlite')
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.manager = ESRSManager(self.db_path)
        # Verify db_path in manager (it might have been changed by __init__)
        # But wait, if I pass absolute path, it should be respected.
        
        self.manager.init_assessments_table()
        
        # Setup Flask test client
        app.config['TESTING'] = True
        app.secret_key = 'test_secret'
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_manager_direct_update(self):
        print("\nTesting Manager Direct Update...")
        company_id = 1
        code = 'E1'
        
        success = self.manager.update_assessment(
            company_id, code, 'in_progress', 'General Note',
            governance_notes='Gov Note',
            strategy_notes='Strat Note',
            impact_risk_notes='Risk Note',
            metrics_notes='Metric Note'
        )
        self.assertTrue(success)
        
        details = self.manager.get_assessment_details(company_id, code)
        self.assertEqual(details['status'], 'in_progress')
        self.assertEqual(details['notes'], 'General Note')
        self.assertEqual(details['governance_notes'], 'Gov Note')
        self.assertEqual(details['strategy_notes'], 'Strat Note')
        self.assertEqual(details['impact_risk_notes'], 'Risk Note')
        self.assertEqual(details['metrics_notes'], 'Metric Note')
        print("Manager Direct Update Verified!")

    def test_route_update(self):
        print("\nTesting Route Update via Flask Client...")
        # Mock session
        with self.client.session_transaction() as sess:
            sess['user'] = 'testuser'
            sess['company_id'] = 1
            
        # Temporarily mock MANAGERS in web_app to use our test manager
        # But web_app imports MANAGERS from itself, so we need to patch it
        import web_app
        original_manager = web_app.MANAGERS.get('esrs')
        web_app.MANAGERS['esrs'] = self.manager
        
        try:
            response = self.client.post('/esrs/update/E2', data={
                'status': 'completed',
                'notes': 'Route Note',
                'governance_notes': 'Route Gov',
                'strategy_notes': 'Route Strat',
                'impact_risk_notes': 'Route Risk',
                'metrics_notes': 'Route Metric'
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # Verify in DB
            details = self.manager.get_assessment_details(1, 'E2')
            self.assertEqual(details['status'], 'completed')
            self.assertEqual(details['notes'], 'Route Note')
            self.assertEqual(details['governance_notes'], 'Route Gov')
            self.assertEqual(details['strategy_notes'], 'Route Strat')
            self.assertEqual(details['impact_risk_notes'], 'Route Risk')
            self.assertEqual(details['metrics_notes'], 'Route Metric')
            print("Route Update Verified!")
            
        finally:
            # Restore
            if original_manager:
                web_app.MANAGERS['esrs'] = original_manager
            else:
                del web_app.MANAGERS['esrs']

if __name__ == '__main__':
    unittest.main()
