import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def init_license_table():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        # Try to find it in alternative location or just print cwd
        print(f"CWD: {os.getcwd()}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create licenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
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
    
    print("Licenses table created or already exists.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_license_table()
