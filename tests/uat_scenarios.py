
import unittest
import sqlite3
import os
import sys
import time
import logging

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from backend.modules.environmental.carbon_manager import CarbonManager

class UATScenarios(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Initialize test environment once"""
        cls.db_path = os.path.join(project_root, 'tests', 'uat_test.db')
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
            
        # Create minimal required schema (companies table)
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        # Create test companies
        cursor.execute("INSERT INTO companies (id, name) VALUES (1, 'Company A')")
        cursor.execute("INSERT INTO companies (id, name) VALUES (2, 'Company B')")
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if os.path.exists(cls.db_path):
            try:
                os.remove(cls.db_path)
            except PermissionError:
                pass

    def setUp(self):
        """Per-test setup"""
        self.manager_a = CarbonManager(db_path=self.db_path, company_id=1)
        self.manager_b = CarbonManager(db_path=self.db_path, company_id=2)

    def test_scenario_1_tenant_isolation(self):
        """
        UAT Scenario 1: Verify Multi-Tenant Data Isolation.
        User A adds data. User B should NOT see it.
        """
        logging.info("Starting UAT Scenario 1: Tenant Isolation")
        
        # 1. Company A adds a record
        logging.info("Step 1: Company A adding carbon emission record...")
        self.manager_a.execute_update("""
            INSERT INTO scope1_emissions (company_id, year, emission_source, total_emissions)
            VALUES (?, ?, ?, ?)
        """, (1, 2024, 'Generator A', 100.0))
        
        # 2. Company B tries to fetch records
        logging.info("Step 2: Company B fetching records...")
        # Direct SQL via manager (simulating internal logic)
        rows_b = self.manager_b.execute_query("SELECT * FROM scope1_emissions")
        
        # 3. Assertions
        logging.info(f"Company B found {len(rows_b)} records.")
        self.assertEqual(len(rows_b), 0, "Company B should see 0 records!")
        
        # 4. Verify Company A sees its record
        rows_a = self.manager_a.execute_query("SELECT * FROM scope1_emissions")
        logging.info(f"Company A found {len(rows_a)} records.")
        self.assertEqual(len(rows_a), 1, "Company A should see 1 record.")
        self.assertEqual(rows_a[0]['total_emissions'], 100.0)
        
        logging.info("✅ UAT Scenario 1 Passed: Data is strictly isolated.")

    def test_scenario_3_reporting_performance(self):
        """
        UAT Scenario 3: Reporting Performance with Large Dataset.
        Insert 10,000 records and measure fetch time.
        Target: < 10 seconds.
        """
        logging.info("Starting UAT Scenario 3: Reporting Performance")
        
        # 1. Bulk Insert 10,000 records for Company A
        logging.info("Step 1: Inserting 10,000 records for Company A...")
        data = []
        for i in range(10000):
            data.append((1, 2024, f'Source {i}', 50.0))
            
        start_insert = time.time()
        
        # Use a direct connection for bulk insert speed (bypassing manager overhead for setup)
        conn = sqlite3.connect(self.db_path)
        conn.executemany("""
            INSERT INTO scope1_emissions (company_id, year, emission_source, total_emissions)
            VALUES (?, ?, ?, ?)
        """, data)
        conn.commit()
        conn.close()
        
        duration_insert = time.time() - start_insert
        logging.info(f"Inserted 10,000 records in {duration_insert:.2f} seconds.")
        
        # 2. Measure Query Performance (Simulate Report Generation)
        logging.info("Step 2: Generating Report (Aggregating Data)...")
        start_query = time.time()
        
        # Complex query: Sum by source, filter by year, etc.
        # Note: CarbonManager.execute_query injects company_id=1 automatically
        results = self.manager_a.execute_query("""
            SELECT count(*) as count, sum(total_emissions) as total 
            FROM scope1_emissions 
            WHERE year = 2024
        """)
        
        duration_query = time.time() - start_query
        logging.info(f"Query executed in {duration_query:.4f} seconds.")
        
        # 3. Assertions
        count = results[0]['count']
        total = results[0]['total']
        
        # Note: 1 record from previous test + 10000 new ones = 10001
        self.assertTrue(count >= 10000, f"Expected >= 10000 records, got {count}")
        self.assertTrue(duration_query < 10.0, f"Performance failed: {duration_query}s > 10s")
        
        logging.info(f"✅ UAT Scenario 3 Passed: Query took {duration_query:.4f}s (Limit: 10s)")

if __name__ == '__main__':
    unittest.main()
