import sqlite3
import os

# Define DB Path explicitly
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_db():
    print(f"Fixing database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create Rate Limits Table
        print("Creating rate_limits table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0,
                UNIQUE(resource_type, identifier)
            )
        """)
        
        # Check if table exists now
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rate_limits'")
        if cursor.fetchone():
            print("✅ Table 'rate_limits' exists.")
        else:
            print("❌ Failed to create table 'rate_limits'.")
            
        conn.commit()
        conn.close()
        print("Database fix completed.")

    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_db()
