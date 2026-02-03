import unittest
import sqlite3
import os
import sys
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from security.core.super_user_protection import check_delete_protection, check_password_change_protection

class TestSuperAdminProtection(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_super_protection.db"
        self._init_db()
        
    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except:
                pass

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create Users Table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Create Roles tables
        cursor.execute("CREATE TABLE roles (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE user_roles (user_id INTEGER, role_id INTEGER)")
        
        # Create Audit Logs (needed by AuditManager)
        cursor.execute("""
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER
            )
        """)
        
        # Add users
        # 1. Normal User
        cursor.execute("INSERT INTO users (username) VALUES ('normal_user')")
        self.normal_user_id = cursor.lastrowid
        
        # 2. Super Admin User
        cursor.execute("INSERT INTO users (username) VALUES ('super_admin')")
        self.super_user_id = cursor.lastrowid
        
        # 3. Actor (Admin)
        cursor.execute("INSERT INTO users (username) VALUES ('admin_actor')")
        self.actor_id = cursor.lastrowid
        
        # Roles
        cursor.execute("INSERT INTO roles (name) VALUES ('Super Admin')")
        super_role_id = cursor.lastrowid
        cursor.execute("INSERT INTO roles (name) VALUES ('User')")
        user_role_id = cursor.lastrowid
        
        # Assign roles
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (self.super_user_id, super_role_id))
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (self.normal_user_id, user_role_id))
        
        conn.commit()
        conn.close()

    def test_delete_normal_user(self):
        """Test deleting a normal user (should always be allowed)."""
        can_delete, msg = check_delete_protection(self.db_path, 'normal_user', self.actor_id)
        self.assertTrue(can_delete, f"Normal user should be deletable: {msg}")

    def test_delete_super_admin_flow(self):
        """Test the 2-stage approval flow for super admin deletion."""
        target_user = 'super_admin'
        
        # 1. First Attempt: Should fail and create pending request
        can_delete, msg = check_delete_protection(self.db_path, target_user, self.actor_id)
        self.assertFalse(can_delete, "First attempt should fail")
        self.assertIn("GÜVENLİK UYARISI", msg)
        
        # Verify request created in DB
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM super_admin_approvals WHERE target_username=?", (target_user,))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        conn.close()
        
        # 2. Second Attempt: Should succeed
        can_delete_2, msg_2 = check_delete_protection(self.db_path, target_user, self.actor_id)
        self.assertTrue(can_delete_2, f"Second attempt should succeed: {msg_2}")
        
        # Verify request consumed
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM super_admin_approvals WHERE target_username=?", (target_user,))
        row = cur.fetchone()
        self.assertIsNone(row, "Approval record should be consumed")
        conn.close()

    def test_password_change_flow(self):
        """Test the 2-stage approval flow for super admin password change."""
        target_user = 'super_admin'
        
        # 1. First Attempt
        can_change, msg = check_password_change_protection(self.db_path, target_user, "newpass", self.actor_id)
        self.assertFalse(can_change)
        
        # 2. Second Attempt
        can_change_2, msg_2 = check_password_change_protection(self.db_path, target_user, "newpass", self.actor_id)
        self.assertTrue(can_change_2)

    def test_root_super_admin_protection(self):
        """Test that __super__ can never be deleted."""
        can_delete, msg = check_delete_protection(self.db_path, '__super__', self.actor_id)
        self.assertFalse(can_delete)
        self.assertIn("Root Super Admin cannot be deleted", msg)

if __name__ == '__main__':
    unittest.main()
