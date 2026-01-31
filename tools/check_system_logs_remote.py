
import sqlite3
import os
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_system_logs():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_logs'")
        if not cur.fetchone():
            print("Table 'system_logs' DOES NOT EXIST.")
            
            # Create table
            print("Creating 'system_logs' table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    module TEXT,
                    message TEXT NOT NULL,
                    user_id INTEGER,
                    company_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Table created.")
        else:
            print("Table 'system_logs' EXISTS.")

        # Check row count
        cur.execute("SELECT COUNT(*) FROM system_logs")
        count = cur.fetchone()[0]
        print(f"Row count: {count}")

        # Insert test log
        print("Inserting test log entry...")
        cur.execute("""
            INSERT INTO system_logs (level, module, message, user_id, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, ('INFO', 'TestScript', 'Test log entry from check script', 1))
        conn.commit()
        print("Test log inserted.")

        # Verify insertion
        cur.execute("SELECT * FROM system_logs ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        print(f"Last log: {row}")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_system_logs()
