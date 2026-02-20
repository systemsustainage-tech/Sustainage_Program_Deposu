import sqlite3
import os
import sys

# Add parent dir to path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'sdg_desktop.sqlite')

def update_schema():
    print(f"Connecting to {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'")
    if not cursor.fetchone():
        print("Creating audit_logs table...")
        cursor.execute("""
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(company_id) REFERENCES companies(id)
            )
        """)
    else:
        print("audit_logs table exists. Checking columns...")
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id column...")
            try:
                # SQLite supports ADD COLUMN
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN company_id INTEGER REFERENCES companies(id)")
            except Exception as e:
                print(f"Error adding company_id: {e}")
                
        if 'resource_type' not in columns and 'resource' not in columns:
             print("Adding resource_type column...")
             try:
                 cursor.execute("ALTER TABLE audit_logs ADD COLUMN resource_type TEXT")
             except Exception as e:
                 print(f"Error adding resource_type: {e}")

        if 'resource_id' not in columns:
             print("Adding resource_id column...")
             try:
                 cursor.execute("ALTER TABLE audit_logs ADD COLUMN resource_id INTEGER")
             except Exception as e:
                 print(f"Error adding resource_id: {e}")

        if 'details' not in columns:
             print("Adding details column...")
             try:
                 cursor.execute("ALTER TABLE audit_logs ADD COLUMN details TEXT")
             except Exception as e:
                 print(f"Error adding details: {e}")

        if 'ip_address' not in columns:
             print("Adding ip_address column...")
             try:
                 cursor.execute("ALTER TABLE audit_logs ADD COLUMN ip_address TEXT")
             except Exception as e:
                 print(f"Error adding ip_address: {e}")

    conn.commit()
    conn.close()
    print("Schema update completed.")

if __name__ == "__main__":
    update_schema()
