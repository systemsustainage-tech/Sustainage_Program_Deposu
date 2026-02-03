import unittest
import sqlite3
import os
import sys
import logging
from datetime import datetime

# Add project root and backend to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Import Managers
from backend.modules.environmental.carbon_manager import CarbonManager
from backend.modules.social.social_manager import SocialManager
# Add other managers if needed

print(f"DEBUG: CarbonManager loaded from {CarbonManager.__module__}")
import inspect
try:
    print(f"DEBUG: CarbonManager file: {inspect.getfile(CarbonManager)}")
    print(f"DEBUG: CarbonManager.get_dashboard_stats source: {inspect.getsource(CarbonManager.get_dashboard_stats)}")
except:
    import traceback
    traceback.print_exc()

class TestMultitenancyIsolation(unittest.TestCase):
    """
    Tests data isolation between different companies (tenants).
    Ensures that data belonging to Company A is not accessible by Company B.
    """

    def setUp(self):
        # Use an in-memory database for speed and isolation, 
        # but we need to create the schema first.
        # Alternatively, use a temporary file.
        self.db_path = os.path.abspath("test_multitenancy.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.init_db()
        
        # Initialize Managers with test DB
        self.carbon_manager = CarbonManager(self.db_path)
        self.social_manager = SocialManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Create Companies Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        
        # 2. Create Carbon Emissions Table (Simplified for testing)
        # Note: Using the schema inferred from CarbonManager
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scope1_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                year INTEGER,
                emission_source TEXT,
                fuel_type TEXT,
                fuel_consumption REAL,
                fuel_unit TEXT,
                emission_factor REAL,
                total_emissions REAL,
                invoice_date TEXT,
                due_date TEXT,
                supplier TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Create Social/Labor Audits Table (Simplified)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fair_labor_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                audit_date TEXT,
                auditor TEXT,
                score REAL,
                findings TEXT,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Insert Test Companies
        cursor.execute("INSERT INTO companies (id, name) VALUES (1, 'Company A')")
        cursor.execute("INSERT INTO companies (id, name) VALUES (2, 'Company B')")
        
        conn.commit()
        conn.close()

    def test_carbon_data_isolation(self):
        """Test that carbon data is isolated by company_id"""
        logging.info("Testing Carbon Data Isolation...")
        
        # Add data for Company 1
        result1 = self.carbon_manager.add_scope1_emission(
            company_id=1,
            year=2024,
            emission_source="Generator A",
            fuel_type="Diesel",
            fuel_consumption=1000,
            fuel_unit="L",
            emission_factor=2.6
        )
        self.assertTrue(result1, "Failed to add emission for Company 1")
        
        # Add data for Company 2
        result2 = self.carbon_manager.add_scope1_emission(
            company_id=2,
            year=2024,
            emission_source="Generator B",
            fuel_type="Diesel",
            fuel_consumption=500,
            fuel_unit="L",
            emission_factor=2.6
        )
        self.assertTrue(result2, "Failed to add emission for Company 2")
        
        # Check DB content manually for debugging
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scope1_emissions")
        rows = cursor.fetchall()
        logging.info(f"DB Content: {rows}")
        
        # Mimic get_dashboard_stats query
        cursor.execute("SELECT SUM(total_emissions) FROM scope1_emissions WHERE company_id = ?", (1,))
        sum_val = cursor.fetchone()[0]
        logging.info(f"Manual SUM for company 1: {sum_val}")
        
        conn.close()
        
        # Verify Company 1 sees only its data
        print(f"DEBUG: Calling get_dashboard_stats for company 1 on instance {self.carbon_manager}")
        stats_c1 = self.carbon_manager.get_dashboard_stats(company_id=1)
        print(f"DEBUG: stats_c1 result: {stats_c1}")
        # CarbonManager.get_dashboard_stats returns {'total_co2e': ..., 'scope1': ...}
        # Note: add_scope1_emission calculates total_emissions passed to it.
        # We passed 2600.
        self.assertEqual(stats_c1['scope1'], 2600.0, "Company 1 should see 2600.0 emissions")
        
        # Verify Company 2 sees only its data
        stats_c2 = self.carbon_manager.get_dashboard_stats(company_id=2)
        self.assertEqual(stats_c2['scope1'], 1300.0, "Company 2 should see 1300.0 emissions")
        
        # Verify cross-access is impossible (logic check)
        # If we query recent records for Company 1, we should not see Company 2's record
        records_c1 = self.carbon_manager.get_recent_records(company_id=1)
        self.assertEqual(len(records_c1), 1)
        self.assertEqual(records_c1[0]['quantity'], 1000)
        
        records_c2 = self.carbon_manager.get_recent_records(company_id=2)
        self.assertEqual(len(records_c2), 1)
        self.assertEqual(records_c2[0]['quantity'], 500)

    def test_social_data_isolation(self):
        """Test that social module data is isolated"""
        logging.info("Testing Social Data Isolation...")
        
        # SocialManager might expect table 'fair_labor_audits'
        # Let's insert manually if add method is complex or just use manager if simple.
        # Checking SocialManager code... assuming add_labor_audit exists or we insert manually.
        # I'll insert manually to be safe and test the 'get' method which is the critical part for isolation.
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fair_labor_audits (company_id, audit_date, auditor, score, status)
            VALUES (1, '2024-01-01', 'Auditor A', 85.0, 'Completed')
        """)
        
        cursor.execute("""
            INSERT INTO fair_labor_audits (company_id, audit_date, auditor, score, status)
            VALUES (2, '2024-01-02', 'Auditor B', 92.0, 'Completed')
        """)
        conn.commit()
        conn.close()
        
        # Verify Company 1
        audits_c1 = self.social_manager.get_labor_audits(company_id=1)
        self.assertEqual(len(audits_c1), 1)
        self.assertEqual(audits_c1[0]['auditor'], 'Auditor A')
        
        # Verify Company 2
        audits_c2 = self.social_manager.get_labor_audits(company_id=2)
        self.assertEqual(len(audits_c2), 1)
        self.assertEqual(audits_c2[0]['auditor'], 'Auditor B')

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    unittest.main()
