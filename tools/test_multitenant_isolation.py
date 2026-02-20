import os
import sys
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

try:
    from core.base_manager import BaseTenantManager
except ImportError:
    # If running from tools/, adjust path
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
    from backend.core.base_manager import BaseTenantManager
    from backend.core.database_manager import DatabaseManager

class TestMultiTenantIsolation(unittest.TestCase):
    def setUp(self):
        # Reset Singleton to ensure we use our temp DB
        DatabaseManager._instance = None
        
        # Use a unique temp file for DB to avoid locking issues
        import uuid
        self.temp_db = os.path.abspath(f"test_isolation_{uuid.uuid4().hex}.db")
        
        conn = sqlite3.connect(self.temp_db)
        conn.execute("CREATE TABLE test_items (id INTEGER PRIMARY KEY, name TEXT, company_id INTEGER)")
        conn.execute("INSERT INTO test_items (name, company_id) VALUES ('Item A', 1)")
        conn.execute("INSERT INTO test_items (name, company_id) VALUES ('Item B', 2)")
        conn.commit()
        conn.close()
        
        self.manager = BaseTenantManager(self.temp_db)

    def tearDown(self):
        # Close connections in pool
        if hasattr(self, 'manager') and self.manager.db:
             while not self.manager.db._pool.empty():
                try:
                    conn = self.manager.db._pool.get_nowait()
                    conn.close()
                except:
                    pass

        if os.path.exists(self.temp_db):
            try:
                os.remove(self.temp_db)
            except PermissionError:
                print(f"Warning: Could not remove {self.temp_db}")

    def test_select_isolation(self):
        print("\nTesting SELECT Isolation...")
        # Context: Company 1
        with patch('flask.g', MagicMock(company_id=1)):
            # 1. Explicit argument
            results = self.manager.select("test_items", company_id=1)
            print(f"  Explicit ID=1 result count: {len(results)}")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['name'], 'Item A')
            
            # 2. Flask G context (via _ensure_context)
            results_g = self.manager.select("test_items")
            print(f"  Flask.g ID=1 result count: {len(results_g)}")
            self.assertEqual(len(results_g), 1)
            self.assertEqual(results_g[0]['name'], 'Item A')

    def test_cross_tenant_access_denied(self):
        print("\nTesting Cross-Tenant Access Denial...")
        # Company 1 trying to see Company 2
        with patch('flask.g', MagicMock(company_id=1)):
             # Even if we explicitly ask for company_id=2 in WHERE, the manager enforces company_id=1 AND ...
             results = self.manager.select("test_items", where="company_id = 2")
             # The query becomes: SELECT * FROM test_items WHERE company_id = 1 AND (company_id = 2)
             # Should return empty
             print(f"  Company 1 asking for Company 2 data result count: {len(results)}")
             self.assertEqual(len(results), 0)

    def test_raw_query_injection(self):
        print("\nTesting Raw Query Injection...")
        # Test execute_query injection
        with patch('flask.g', MagicMock(company_id=2)):
            # Attempt to select ALL items
            results = self.manager.execute_query("SELECT * FROM test_items")
            # Should inject WHERE company_id = 2
            print(f"  Raw SELECT * with Company 2 context result count: {len(results)}")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['name'], 'Item B')

    def test_insert_injection(self):
         print("\nTesting INSERT Injection...")
         with patch('flask.g', MagicMock(company_id=1)):
             # Insert without company_id
             self.manager.execute_update("INSERT INTO test_items (name) VALUES ('Item C')")
             
             # Verify it got company_id=1
             conn = sqlite3.connect(self.temp_db)
             cur = conn.cursor()
             cur.execute("SELECT company_id FROM test_items WHERE name='Item C'")
             row = cur.fetchone()
             print(f"  Inserted 'Item C' assigned company_id: {row[0]}")
             self.assertEqual(row[0], 1)
             conn.close()

if __name__ == '__main__':
    unittest.main()
