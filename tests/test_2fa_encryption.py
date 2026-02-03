import unittest
import sqlite3
import os
import sys
import pyotp
import tempfile
from cryptography.fernet import Fernet

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'backend'))

from backend.security.core.enhanced_2fa import enable_totp_for_user, verify_totp_code, _decrypt_secret, _encrypt_secret

class Test2FAEncryption(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                is_superadmin INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                is_admin INTEGER DEFAULT 0,
                must_change_password INTEGER DEFAULT 0,
                last_login INTEGER,
                deleted_at INTEGER,
                totp_secret TEXT,
                totp_enabled INTEGER DEFAULT 0,
                backup_codes TEXT
            )
        """)
        # Create a user
        self.username = "testuser"
        self.cursor.execute("INSERT INTO users (username) VALUES (?)", (self.username,))
        self.conn.commit()
        
    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_encryption(self):
        # 1. Enable 2FA
        ok, msg, plain_secret, qr = enable_totp_for_user(self.db_path, self.username)
        self.assertTrue(ok)
        self.assertIsNotNone(plain_secret)
        
        # 2. Check DB content
        self.cursor.execute("SELECT totp_secret FROM users WHERE username=?", (self.username,))
        row = self.cursor.fetchone()
        db_secret = row[0]
        
        # 3. Verify DB secret is encrypted (not equal to plain secret)
        self.assertNotEqual(db_secret, plain_secret)
        self.assertNotEqual(len(db_secret), len(plain_secret)) # Encrypted should be longer
        
        # 4. Verify decryption works
        decrypted = _decrypt_secret(db_secret)
        self.assertEqual(decrypted, plain_secret)
        
        # 5. Verify OTP code verification works
        totp = pyotp.TOTP(plain_secret)
        code = totp.now()
        ok, msg = verify_totp_code(self.db_path, self.username, code)
        self.assertTrue(ok, f"Verification failed with message: {msg}")
        
    def test_backward_compatibility(self):
        # Insert a PLAIN text secret manually
        plain_secret = pyotp.random_base32()
        self.cursor.execute("UPDATE users SET totp_secret=? WHERE username=?", (plain_secret, self.username))
        self.conn.commit()
        
        # Try to verify (should fallback to plain text)
        totp = pyotp.TOTP(plain_secret)
        code = totp.now()
        ok, msg = verify_totp_code(self.db_path, self.username, code)
        self.assertTrue(ok, "Backward compatibility failed")

if __name__ == '__main__':
    unittest.main()
