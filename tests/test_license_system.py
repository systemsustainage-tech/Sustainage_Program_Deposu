import unittest
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import jwt

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from yonetim.license_manager import LicenseManager

class TestLicenseSystem(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_license.db"
        self._init_db()
        self.lm = LicenseManager(self.db_path)
        
    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except:
                pass

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create companies table (simplified)
        cursor.execute("CREATE TABLE companies (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO companies (name) VALUES ('Test Corp')")
        self.company_id = cursor.lastrowid
        
        # Create licenses table
        cursor.execute("""
            CREATE TABLE licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                license_key TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                max_users INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        conn.commit()
        conn.close()

    def test_generate_license(self):
        """Test generating a valid license."""
        result = self.lm.generate_license(self.company_id, duration_days=30, max_users=10)
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['license_key'])
        
        # Verify in DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM licenses WHERE company_id=?", (self.company_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[6], 'active') # status

    def test_verify_license_valid(self):
        """Test verifying a valid license."""
        res = self.lm.generate_license(self.company_id)
        key = res['license_key']
        
        is_valid, msg, payload = self.lm.verify_license_key(key)
        self.assertTrue(is_valid, f"Verification failed: {msg}")
        self.assertEqual(payload['company_id'], self.company_id)

    def test_verify_license_expired(self):
        """Test verifying an expired license."""
        # Manually insert expired license
        # Note: JWT_SECRET is hardcoded in LicenseManager as "SUSTAINAGE_SDG_LICENSE_SECRET_KEY_2025"
        expired_key = jwt.encode({
            'company_id': self.company_id,
            'exp': int((datetime.now() - timedelta(days=1)).timestamp())
        }, "SUSTAINAGE_SDG_LICENSE_SECRET_KEY_2025", algorithm="HS256")
        
        # We need to insert it into DB too, because verify checks DB status
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO licenses (company_id, license_key, status)
            VALUES (?, ?, 'active')
        """, (self.company_id, expired_key))
        conn.commit()
        conn.close()
        
        is_valid, msg, payload = self.lm.verify_license_key(expired_key)
        self.assertFalse(is_valid)
        self.assertIn("expired", msg)

    def test_verify_license_revoked(self):
        """Test verifying a revoked license."""
        res = self.lm.generate_license(self.company_id)
        key = res['license_key']
        
        # Revoke in DB
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE licenses SET status='revoked' WHERE license_key=?", (key,))
        conn.commit()
        conn.close()
        
        is_valid, msg, payload = self.lm.verify_license_key(key)
        self.assertFalse(is_valid)
        self.assertIn("revoked", msg)

    def test_get_active_license(self):
        """Test retrieving the active license."""
        res = self.lm.generate_license(self.company_id)
        key = res['license_key']
        
        fetched_key = self.lm.get_active_license(self.company_id)
        self.assertEqual(key, fetched_key)

if __name__ == '__main__':
    unittest.main()
