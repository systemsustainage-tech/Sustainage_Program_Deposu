
import unittest
import sqlite3
import os
import sys
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from yonetim.yönetim_gui import YonetimGUI
from config.database import DB_PATH

class TestSuperAdminIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temp super admin user
        cls.conn = sqlite3.connect(DB_PATH)
        cls.cur = cls.conn.cursor()
        
        # Insert test user - provide all required fields (first_name, last_name are NOT NULL)
        cls.cur.execute("INSERT OR IGNORE INTO users (id, username, email, password_hash, first_name, last_name) VALUES (999, 'test_super', 'super@test.com', 'hash', 'Test', 'Super')")
        cls.cur.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (999, 1)") # role_id 1 = super_admin
        
        # Insert test admin user
        cls.cur.execute("INSERT OR IGNORE INTO users (id, username, email, password_hash, first_name, last_name) VALUES (998, 'test_admin', 'admin@test.com', 'hash', 'Test', 'Admin')")
        cls.cur.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (998, 2)") # role_id 2 = admin
        
        cls.conn.commit()
        cls.conn.close()

    @classmethod
    def tearDownClass(cls):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id IN (999, 998)")
        cur.execute("DELETE FROM user_roles WHERE user_id IN (999, 998)")
        conn.commit()
        conn.close()

    def test_is_super_admin_true(self):
        # Mock parent
        parent = MagicMock()
        
        # Patch setup_ui to avoid GUI creation
        with patch.object(YonetimGUI, 'setup_ui'), \
             patch.object(YonetimGUI, 'create_all_tabs'), \
             patch.object(YonetimGUI, 'create_welcome_page'):
            
            gui = YonetimGUI(parent, current_user_id=999)
            self.assertTrue(gui._is_super_admin())

    def test_is_super_admin_false(self):
        # Mock parent
        parent = MagicMock()
        
        # Patch setup_ui to avoid GUI creation
        with patch.object(YonetimGUI, 'setup_ui'), \
             patch.object(YonetimGUI, 'create_all_tabs'), \
             patch.object(YonetimGUI, 'create_welcome_page'):
            
            gui = YonetimGUI(parent, current_user_id=998)
            self.assertFalse(gui._is_super_admin())

    def test_get_user_info(self):
        # Mock parent
        parent = MagicMock()
        
        # Patch setup_ui to avoid GUI creation
        with patch.object(YonetimGUI, 'setup_ui'), \
             patch.object(YonetimGUI, 'create_all_tabs'), \
             patch.object(YonetimGUI, 'create_welcome_page'):
            
            gui = YonetimGUI(parent, current_user_id=999)
            user_info = gui._get_current_user_info()
            self.assertIsNotNone(user_info)
            self.assertEqual(user_info[1], 'test_super') # username is index 1

if __name__ == '__main__':
    unittest.main()
