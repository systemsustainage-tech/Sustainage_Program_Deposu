import sys
import os
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Flask before importing database
sys.modules['flask'] = MagicMock()
from flask import g, has_request_context

# Now import TenantAwareDB
from backend.core.database import TenantAwareDB

class TestTenantAwareDBInsert(unittest.TestCase):
    def setUp(self):
        self.db = TenantAwareDB(':memory:')
        # Setup table
        self.db.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT, company_id INTEGER)")
        self.db.execute("CREATE TABLE companies (id INTEGER PRIMARY KEY, name TEXT)") # Global table

    def tearDown(self):
        self.db.close()

    @patch('backend.core.database.has_request_context')
    @patch('backend.core.database.g')
    def test_insert_injection(self, mock_g, mock_has_context):
        # Setup context
        mock_has_context.return_value = True
        mock_g.company_id = 99
        
        # Test INSERT
        sql = "INSERT INTO test_table (name) VALUES (?)"
        params = ("test_item",)
        
        # We need to spy on the cursor to see the actual SQL executed?
        # Or just verify the data inserted has company_id=99
        
        self.db.execute(sql, params)
        
        # Verify
        cursor = self.db._get_conn().cursor()
        cursor.execute("SELECT * FROM test_table")
        row = cursor.fetchone()
        
        self.assertEqual(row[1], "test_item")
        self.assertEqual(row[2], 99) # Should be injected
        print("INSERT Injection Test: SUCCESS")

    @patch('backend.core.database.has_request_context')
    @patch('backend.core.database.g')
    def test_insert_global_table(self, mock_g, mock_has_context):
        # Setup context
        mock_has_context.return_value = True
        mock_g.company_id = 99
        
        # Test INSERT into global table
        sql = "INSERT INTO companies (name) VALUES (?)"
        params = ("Global Corp",)
        
        # This table DOES NOT have company_id column, so injection would fail SQL if attempted.
        # But we expect it to SKIP injection.
        
        self.db.execute(sql, params)
        
        cursor = self.db._get_conn().cursor()
        cursor.execute("SELECT * FROM companies")
        row = cursor.fetchone()
        
        self.assertEqual(row[1], "Global Corp")
        # If injection happened, it would have tried to insert company_id and likely failed 
        # (unless we created the table with company_id, which we didn't in setUp for companies)
        # Actually in setUp I created companies with (id, name).
        print("Global Table Skip Test: SUCCESS")

    @patch('backend.core.database.has_request_context')
    @patch('backend.core.database.g')
    def test_insert_existing_company_id(self, mock_g, mock_has_context):
        mock_has_context.return_value = True
        mock_g.company_id = 99
        
        # Test INSERT where company_id is already provided
        sql = "INSERT INTO test_table (name, company_id) VALUES (?, ?)"
        params = ("Manual Corp", 55) # Override
        
        self.db.execute(sql, params)
        
        cursor = self.db._get_conn().cursor()
        cursor.execute("SELECT * FROM test_table WHERE name='Manual Corp'")
        row = cursor.fetchone()
        
        self.assertEqual(row[2], 55) # Should be respected, not overwritten or double-injected
        print("Existing company_id Test: SUCCESS")

if __name__ == '__main__':
    unittest.main()
