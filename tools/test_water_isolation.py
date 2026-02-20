
import sys
import os
import unittest
import logging
from datetime import date
from flask import Flask

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.modules.environmental.water_manager import WaterManager
from backend.config.database import DB_PATH

app = Flask(__name__)

class TestWaterManagerIsolation(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        
        self.manager = WaterManager(DB_PATH)
        # Use test company IDs
        self.company_a = 999991
        self.company_b = 999992
        
        # Create companies table and test companies (Direct DB access to bypass tenant filter)
        self.manager.db.execute_update("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        self.manager.db.execute_update("INSERT OR IGNORE INTO companies (id, name) VALUES (?, ?)", (self.company_a, 'Company A'))
        self.manager.db.execute_update("INSERT OR IGNORE INTO companies (id, name) VALUES (?, ?)", (self.company_b, 'Company B'))
        
        # Clean up any existing test data
        self.cleanup()

    def tearDown(self):
        self.cleanup()
        # Clean up companies
        self.manager.db.execute_update("DELETE FROM companies WHERE id IN (?, ?)", (self.company_a, self.company_b))
        self.ctx.pop()

    def cleanup(self):
        try:
            # Delete for each company specifically to satisfy tenant filter
            self.manager.execute_update("DELETE FROM water_consumption", company_id=self.company_a)
            self.manager.execute_update("DELETE FROM water_consumption", company_id=self.company_b)
        except Exception as e:
            print(f"Cleanup failed: {e}")

    def test_isolation(self):
        print("\nTesting WaterManager Multi-tenant Isolation...")
        
        # 1. Insert data for Company A
        self.manager.add_water_consumption(
            company_id=self.company_a,
            year=2024,
            month=1,
            consumption_type='Test Water A',
            consumption_amount=100.0,
            unit='m3',
            source='Well',
            cost=500.0
        )
        
        # 2. Insert data for Company B
        self.manager.add_water_consumption(
            company_id=self.company_b,
            year=2024,
            month=1,
            consumption_type='Test Water B',
            consumption_amount=200.0,
            unit='m3',
            source='Mains',
            cost=1000.0
        )
        
        # 3. Verify Company A sees only its data
        # Note: add_consumption might not return the ID, so we query by company_id
        # But get_recent_records uses company_id
        records_a = self.manager.get_recent_records(self.company_a)
        self.assertTrue(len(records_a) >= 1)
        found_a = False
        for r in records_a:
            if r['amount'] == 100.0 and r['type'] == 'Test Water A':
                found_a = True
            # Ensure no Company B data leaks
            self.assertNotEqual(r['type'], 'Test Water B')
            
        self.assertTrue(found_a, "Company A should see its own data")
        
        # 4. Verify Company B sees only its data
        records_b = self.manager.get_recent_records(self.company_b)
        self.assertTrue(len(records_b) >= 1)
        found_b = False
        for r in records_b:
            if r['amount'] == 200.0 and r['type'] == 'Test Water B':
                found_b = True
            # Ensure no Company A data leaks
            self.assertNotEqual(r['type'], 'Test Water A')
            
        self.assertTrue(found_b, "Company B should see its own data")
        
        print("WaterManager Isolation Test PASSED")

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    unittest.main()
