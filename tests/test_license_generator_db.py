import unittest
import os
import sys
import tempfile
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database_manager import DatabaseManager
from backend.modules.super_admin.components.license_generator import LicenseGenerator

class TestLicenseGeneratorDB(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        # Ensure we get a fresh instance by passing the new path
        self.db = DatabaseManager(self.db_path)
        
        # Create tables
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT UNIQUE NOT NULL,
                    license_type TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    contact_email TEXT,
                    contact_phone TEXT,
                    issued_date TEXT NOT NULL,
                    expiry_date TEXT,
                    max_users INTEGER DEFAULT 1,
                    enabled_modules TEXT,
                    hardware_id TEXT,
                    signature TEXT,
                    is_active INTEGER DEFAULT 1,
                    allowed_ips TEXT,
                    allowed_domains TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS license_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    new_value TEXT,
                    performed_by TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (license_id) REFERENCES licenses(id)
                )
            """)
            conn.commit()

        self.generator = LicenseGenerator(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        # DatabaseManager might hold a lock/connection to the file. 
        # In a real test we might want to close connections explicitly or just ignore file deletion errors on Windows.
        try:
            os.unlink(self.db_path)
        except PermissionError:
            pass

    def test_generate_license_success(self):
        result = self.generator.generate_license_key(
            company_name="Test Company",
            license_type="Enterprise",
            duration_days=365,
            max_users=50,
            enabled_modules=["mod1", "mod2"]
        )
        
        self.assertTrue(result['success'])
        self.assertIn('license_key', result)
        license_id = result.get('license_id')
        self.assertIsNotNone(license_id)

        # Verify in DB
        rows = self.db.execute_query("SELECT * FROM licenses WHERE id = ?", (license_id,))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['company_name'], "Test Company")
        self.assertEqual(row['max_users'], 50)
        
        # Verify history
        hist_rows = self.db.execute_query("SELECT * FROM license_history WHERE license_id = ?", (license_id,))
        self.assertEqual(len(hist_rows), 1)
        self.assertEqual(hist_rows[0]['action'], 'created')

if __name__ == '__main__':
    unittest.main()
