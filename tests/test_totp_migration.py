import unittest
import sqlite3
import os
import sys
import tempfile
import shutil

# Add project root to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Now we can import from tools and backend
from tools.migrate_totp_secrets import migrate_secrets
from backend.security.core.enhanced_2fa import _decrypt_secret, _encrypt_secret

class TestTOTPMigration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_db.sqlite')
        
        # Initialize database
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                totp_secret TEXT
            )
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.test_dir)

    def test_migration_encrypts_plain_secret(self):
        """Test that a plain text secret is correctly encrypted."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        username = "testuser"
        
        # Insert plain text secret
        self.cursor.execute("INSERT INTO users (username, totp_secret) VALUES (?, ?)", (username, plain_secret))
        self.conn.commit()
        
        # Run migration
        success = migrate_secrets(self.db_path)
        self.assertTrue(success, "Migration should succeed")
        
        # Verify in DB
        self.cursor.execute("SELECT totp_secret FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        new_secret = row[0]
        
        # Should not be plain anymore
        self.assertNotEqual(new_secret, plain_secret)
        
        # Should be decryptable back to original
        decrypted = _decrypt_secret(new_secret)
        self.assertEqual(decrypted, plain_secret)
        
        # Fernet tokens usually start with gAAAA
        self.assertTrue(new_secret.startswith("gAAAA"), "Encrypted secret should start with Fernet prefix")

    def test_migration_reencrypts_encrypted_secret(self):
        """Test that an already encrypted secret is re-encrypted (rotated) correctly."""
        plain_secret = "OZSXE6ZAON2GK5TU"
        username = "testuser2"
        
        # Encrypt initially
        initial_encrypted = _encrypt_secret(plain_secret)
        
        # Insert encrypted secret
        self.cursor.execute("INSERT INTO users (username, totp_secret) VALUES (?, ?)", (username, initial_encrypted))
        self.conn.commit()
        
        # Run migration
        success = migrate_secrets(self.db_path)
        self.assertTrue(success, "Migration should succeed")
        
        # Verify in DB
        self.cursor.execute("SELECT totp_secret FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        new_secret = row[0]
        
        # Should still be decryptable
        decrypted = _decrypt_secret(new_secret)
        self.assertEqual(decrypted, plain_secret)
        
        # It might be different from initial_encrypted because Fernet uses random IVs
        # But both should decrypt to the same plain text
        
    def test_migration_handles_empty_secret(self):
        """Test that users with no secret are ignored."""
        username = "nosecret"
        
        self.cursor.execute("INSERT INTO users (username, totp_secret) VALUES (?, ?)", (username, None))
        self.conn.commit()
        
        success = migrate_secrets(self.db_path)
        self.assertTrue(success)
        
        self.cursor.execute("SELECT totp_secret FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        self.assertIsNone(row[0])

if __name__ == '__main__':
    unittest.main()
