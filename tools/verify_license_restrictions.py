import sys
import os
import json
import time
import sqlite3
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.yonetim.license_manager import LicenseManager
from backend.config.database import DB_PATH

class TestLicenseRestrictions(unittest.TestCase):
    def setUp(self):
        self.lm = LicenseManager(DB_PATH)
        self.test_company_id = 99999
        self.conn = sqlite3.connect(DB_PATH)
        
        # Clean up previous test data
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM licenses WHERE company_id = ?", (self.test_company_id,))
        self.conn.commit()

    def tearDown(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM licenses WHERE company_id = ?", (self.test_company_id,))
        self.conn.commit()
        self.conn.close()

    def test_ip_restriction(self):
        print("\n--- Testing IP Restriction ---")
        # Generate license allowed for 127.0.0.1 only
        result = self.lm.generate_license(
            company_id=self.test_company_id,
            allowed_ips=['127.0.0.1']
        )
        key = result['license_key']
        print(f"Generated Key: {key}")

        # Verify logic manually first (integration test for Manager)
        # Check payload
        valid, msg, payload = self.lm.verify_license_key(key)
        self.assertTrue(valid)
        self.assertEqual(payload.get('allowed_ips'), ['127.0.0.1'])
        print("Payload verification successful.")

    def test_abuse_detection(self):
        print("\n--- Testing Abuse Detection ---")
        # Generate normal license
        result = self.lm.generate_license(
            company_id=self.test_company_id
        )
        key = result['license_key']
        
        # Simulate 301 requests
        print("Simulating 305 requests...")
        start_time = time.time()
        for i in range(305):
            is_abusive, reason = self.lm.update_usage_and_check_abuse(key)
            if is_abusive:
                print(f"Abuse detected at request {i+1}: {reason}")
                self.lm.suspend_license(key, reason)
                break
        
        # Check if suspended
        valid, msg, payload = self.lm.verify_license_key(key)
        self.assertFalse(valid)
        self.assertIn("suspended", msg)
        print("License successfully suspended due to abuse.")

if __name__ == '__main__':
    unittest.main()
