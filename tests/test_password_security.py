import unittest
import sqlite3
import os
import sys
import hashlib
import time
import shutil

# Add project root and backend to sys.path
root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'backend'))

from backend.security.core import secure_password

class TestPasswordSecurity(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_security.sqlite"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                failed_attempts INTEGER DEFAULT 0,
                locked_until INTEGER
            )
        """)
        cursor.execute("INSERT INTO users (username, password) VALUES ('testuser', 'dummyhash')")
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_lockout_logic(self):
        username = "testuser"
        
        # 1. Initial state: Not locked
        # secure_password.lockout_check returns (is_allowed, wait_time)
        # Based on implementation: if not locked, returns True, 0
        is_allowed, wait_time = secure_password.lockout_check(self.test_db, username)
        self.assertTrue(is_allowed, "Initial state should be allowed")
        self.assertEqual(wait_time, 0)
        
        # 2. Record failed attempts (Threshold is default 5)
        for i in range(5):
            secure_password.record_failed_login(self.test_db, username, max_attempts=5, lock_seconds=60)
            
        # 3. Should be locked now
        is_allowed, wait_time = secure_password.lockout_check(self.test_db, username)
        self.assertFalse(is_allowed, "Should be locked after max attempts")
        self.assertGreater(wait_time, 0)
        
        # 4. Reset attempts
        secure_password.reset_failed_attempts(self.test_db, username)
        is_allowed, wait_time = secure_password.lockout_check(self.test_db, username)
        self.assertTrue(is_allowed, "Should be allowed after reset")

    def test_verify_legacy_sha256(self):
        # Create a raw SHA-256 hash for "password123"
        pw = "password123"
        sha256_hash = hashlib.sha256(pw.encode()).hexdigest()
        
        # Verify
        ok, needs_rehash = secure_password.verify_password(sha256_hash, pw)
        self.assertTrue(ok)
        self.assertTrue(needs_rehash, "Legacy SHA-256 should request rehash")
        
        # Verify with wrong password
        ok, _ = secure_password.verify_password(sha256_hash, "wrong")
        self.assertFalse(ok)

    def test_verify_migrated_argon2_sha256(self):
        # Simulate the migration process
        pw = "password123"
        original_sha256 = hashlib.sha256(pw.encode()).hexdigest()
        
        # Double hash: Argon2(SHA256(pw))
        # We manually use the logic from verify_password to simulate the DB state
        # But wait, we can use the logic we put in migrate_passwords.py
        # Or better, just use the underlying crypto library to generate the inner hash
        try:
            from backend.yonetim.security.core.crypto import hash_password as argon2_hash
            inner_hash = argon2_hash(original_sha256)
            stored_hash = f"argon2_sha256${inner_hash}"
            
            # Verify
            ok, needs_rehash = secure_password.verify_password(stored_hash, pw)
            self.assertTrue(ok, "Migrated double-hash should verify correctly")
            self.assertFalse(needs_rehash, "Migrated hash is considered secure enough")
            
            # Verify with wrong password
            ok, _ = secure_password.verify_password(stored_hash, "wrong")
            self.assertFalse(ok)
            
        except ImportError:
            self.skipTest("argon2-cffi not installed or crypto module not found")

    def test_new_hash_format(self):
        # Test that new hashes get the argon2$ prefix (or standard format)
        pw = "newpassword"
        h = secure_password.hash_password(pw)
        self.assertTrue(h.startswith("argon2$") or h.startswith("$argon2"), f"Hash should start with argon2 prefix, got: {h}")
        
        # Verify it works
        ok, needs = secure_password.verify_password(h, pw)
        self.assertTrue(ok)
        self.assertFalse(needs)

if __name__ == "__main__":
    unittest.main()
