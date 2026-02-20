import sys
import os
import unittest
import sqlite3
from flask import Flask, g

# Add path to find backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.core.database import TenantAwareDB, GLOBAL_TABLES

class TestTenantAwareDB(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        
        self.db_path = ':memory:'
        self.db = TenantAwareDB(self.db_path)
        
        # Access raw connection for setup
        self.raw_conn = self.db._get_conn()
        self.raw_conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, company_id INTEGER, name TEXT)")
        self.raw_conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)") # Global table
        
        self.raw_conn.execute("INSERT INTO test_table (company_id, name) VALUES (1, 'Company 1 Item')")
        self.raw_conn.execute("INSERT INTO test_table (company_id, name) VALUES (2, 'Company 2 Item')")
        self.raw_conn.execute("INSERT INTO users (id, username) VALUES (1, 'admin')")
        self.raw_conn.commit()

    def tearDown(self):
        self.ctx.pop()

    def test_select_injection(self):
        g.company_id = 1
        
        # 1. Simple SELECT
        cursor = self.db.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        print(f"Rows for Company 1: {[r['name'] for r in rows]}")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Company 1 Item')

    def test_select_with_where(self):
        g.company_id = 2
        
        # 2. SELECT with WHERE
        cursor = self.db.execute("SELECT * FROM test_table WHERE name LIKE ?", ('%Item%',))
        rows = cursor.fetchall()
        print(f"Rows for Company 2: {[r['name'] for r in rows]}")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Company 2 Item')

    def test_global_table_skip(self):
        g.company_id = 1
        
        # 3. Global Table (users)
        cursor = self.db.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)

    def test_update_injection(self):
        g.company_id = 1
        
        # 4. UPDATE
        self.assertEqual(self.db.execute("SELECT name FROM test_table WHERE id=1").fetchone()[0], 'Company 1 Item')
        self.db.execute("UPDATE test_table SET name = ? WHERE id = ?", ('Updated', 1))
        
        # Check result
        row = self.raw_conn.execute("SELECT name FROM test_table WHERE id=1").fetchone()
        self.assertEqual(row[0], 'Updated')
        
        # Verify it didn't touch Company 2 if we tried
        self.db.execute("UPDATE test_table SET name = ? WHERE id = ?", ('Hacked', 2))
        row2 = self.raw_conn.execute("SELECT name FROM test_table WHERE id=2").fetchone()
        self.assertEqual(row2[0], 'Company 2 Item') # Should NOT change

if __name__ == '__main__':
    unittest.main()
