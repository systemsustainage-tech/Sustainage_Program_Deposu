
import unittest
import os
import sys
import sqlite3
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing web_app
sys.modules['flask_compress'] = MagicMock()
mock_limiter = MagicMock()
# Configure limiter.limit to act as a pass-through decorator
def mock_limit(*args, **kwargs):
    def decorator(f):
        return f
    return decorator
mock_limiter.limit.side_effect = mock_limit
# Configure MockLimiter class (used in web_app)
class MockLimiter:
    def __init__(self, *args, **kwargs): pass
    def limit(self, *args, **kwargs):
        def decorator(f): return f
        return decorator

sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter'].Limiter = MockLimiter
sys.modules['flask_limiter.util'] = MagicMock()
sys.modules['flask_talisman'] = MagicMock()

# Import app
from web_app import app

class TestTwoStageApproval(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_two_stage.db'
        self.init_db()
        
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'testkey'
        self.client = app.test_client()
        
        # Patch get_db
        self.patcher = patch('web_app.get_db', side_effect=self.get_test_db)
        self.mock_get_db = self.patcher.start()

        # Patch DB_PATH in super_user_protection because it might use it directly if passed
        # But web_app passes DB_PATH global. We can patch web_app.DB_PATH
        self.db_path_patcher = patch('web_app.DB_PATH', self.db_path)
        self.db_path_patcher.start()
        
        # Also need to patch backend.security.core.super_user_protection._get_connection if needed
        # But web_app passes DB_PATH to _check_two_stage_approval, so passing self.db_path should work
        # provided web_app uses the patched DB_PATH variable. 
        # Since we patched web_app.DB_PATH, it should be fine.

    def tearDown(self):
        self.patcher.stop()
        self.db_path_patcher.stop()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except:
                pass

    def get_test_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                password_hash TEXT,
                first_name TEXT,
                last_name TEXT,
                department TEXT,
                last_login TIMESTAMP,
                is_verified INTEGER DEFAULT 1,
                company_id INTEGER,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Create audit_logs table
        cursor.execute("""
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                user_id INTEGER,
                action VARCHAR(50) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                session_id VARCHAR(100),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create roles and user_roles
        cursor.execute("CREATE TABLE roles (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE user_roles (user_id INTEGER, role_id INTEGER)")
        
        # Create super_admin_approvals (will be created by code if not exists, but good to have)
        
        # Insert Admin User (ID 1)
        cursor.execute("INSERT INTO users (username, password_hash, company_id) VALUES ('admin', 'hash', 1)")
        cursor.execute("INSERT INTO roles (name) VALUES ('super_admin')")
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (1, 1)")
        
        # Insert Target User (ID 2)
        cursor.execute("INSERT INTO users (username, password_hash, company_id) VALUES ('target', 'hash', 1)")
        
        conn.commit()
        conn.close()

    def test_user_delete_two_stage(self):
        # Login as admin
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user'] = 'admin'
            sess['role'] = '__super__' # Pass @admin_required check
            sess['company_id'] = 1
            
        # 1st Attempt: Should create request and fail
        # We need to mock g.company_id for @require_company_context
        # But @require_company_context sets g.company_id from session or user.
        # It relies on session['company_id'] or similar.
        # Let's verify require_company_context implementation if needed.
        # Assuming session['company_id'] is enough.
        
        response = self.client.get('/users/delete/2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check Flash Message (decoded)
        response_text = response.data.decode('utf-8')
        
        # DEBUG: Print flash messages if any
        # Flash messages are usually in the HTML, e.g. <div class="alert ...">Message</div>
        # Or we can check the session if not consumed, but follow_redirects consumes them into the page.
        
        # Let's check if the approval record was created FIRST.
        # If it was created, then the logic ran.
        conn = self.get_test_db()
        approval = conn.execute("SELECT * FROM super_admin_approvals WHERE target_username='target'").fetchone()
        conn.close()
        
        if not approval:
            print("DEBUG: Approval record NOT created.")
            # This means _check_two_stage_approval returned True immediately or failed silently?
        else:
            print(f"DEBUG: Approval record created: {dict(approval)}")
            
        if "GÜVENLİK UYARISI" not in response_text:
            print("DEBUG: Flash message not found in response text.")
            # Write response to file for inspection
            with open('debug_response.html', 'w', encoding='utf-8') as f:
                f.write(response_text)
        
        # Expecting Turkish warning message
        self.assertIn("GÜVENLİK UYARISI", response_text)
        
        # Check user still exists
        conn = self.get_test_db()
        user = conn.execute("SELECT * FROM users WHERE id=2").fetchone()
        self.assertIsNotNone(user)
        
        # Check approval table
        approval = conn.execute("SELECT * FROM super_admin_approvals WHERE target_username='target'").fetchone()
        self.assertIsNotNone(approval)
        self.assertEqual(approval['action_type'], 'USER_DELETE')
        conn.close()
        
        # 2nd Attempt: Should succeed
        response = self.client.get('/users/delete/2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Kullanıcı silindi", response.data.decode('utf-8'))
        
        # Check user deleted
        conn = self.get_test_db()
        user = conn.execute("SELECT * FROM users WHERE id=2").fetchone()
        self.assertIsNone(user)
        conn.close()

if __name__ == '__main__':
    unittest.main()
