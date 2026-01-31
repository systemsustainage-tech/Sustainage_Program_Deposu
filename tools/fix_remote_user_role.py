import sqlite3
import os
import datetime

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_user_and_logs():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # 1. Fix test_user Role
        print("\n--- Fixing test_user Role ---")
        cur.execute("SELECT id FROM users WHERE username='test_user'")
        user_row = cur.fetchone()
        if not user_row:
            print("test_user not found!")
        else:
            user_id = user_row[0]
            cur.execute("SELECT id FROM roles WHERE name='User'")
            role_row = cur.fetchone()
            if not role_row:
                # Create User role if missing
                try:
                    cur.execute("INSERT INTO roles (name, description, display_name) VALUES ('User', 'Standard User', 'Kullanıcı')")
                except sqlite3.OperationalError:
                     # Fallback if display_name doesn't exist (unlikely given error)
                     cur.execute("INSERT INTO roles (name, description) VALUES ('User', 'Standard User')")
                
                role_id = cur.lastrowid
                print("Created 'User' role.")
            else:
                role_id = role_row[0]
            
            # Check if link exists
            cur.execute("SELECT 1 FROM user_roles WHERE user_id=? AND role_id=?", (user_id, role_id))
            if not cur.fetchone():
                cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
                print(f"Assigned 'User' role (id={role_id}) to 'test_user' (id={user_id}).")
            else:
                print("'test_user' already has 'User' role.")
        
        # 2. Fix Audit Logs
        print("\n--- Fixing Audit Logs ---")
        
        # Drop existing table to ensure schema match
        cur.execute("DROP TABLE IF EXISTS audit_logs")
        print("Dropped existing audit_logs table.")

        # Create new table with correct schema (matching AuditLogger and web_app expectations)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id INTEGER,
                details TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                success TEXT DEFAULT 'true',
                error_message TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Removed Foreign Key to avoid issues if companies table missing/different
        
        # Insert a test log
        cur.execute("""
            INSERT INTO audit_logs (username, action, details, timestamp, resource_type, company_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('test_user', 'TEST_LOG_ENTRY', 'This is a test log entry to verify visibility.', datetime.datetime.now(), 'TEST', 1))
        print("Inserted test log entry into audit_logs.")
        
        # Check count
        cur.execute("SELECT COUNT(*) FROM audit_logs")
        count = cur.fetchone()[0]
        print(f"Total rows in audit_logs now: {count}")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_user_and_logs()
