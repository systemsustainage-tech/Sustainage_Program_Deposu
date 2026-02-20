import sqlite3
import sys
import os

if os.name == 'nt':
    DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
else:
    DB_PATH = "/var/www/sustainage/backend/data/sdg_prod.sqlite"

def fix_rate_limits_table():
    print("Fixing rate_limits table (Correct Schema)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Drop table if it exists (to ensure schema correctness)
        cursor.execute("DROP TABLE IF EXISTS rate_limits")
        
        # Create table with correct columns matching RateLimiter class
        cursor.execute("""
            CREATE TABLE rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                window_start TEXT,
                is_blocked INTEGER DEFAULT 0,
                UNIQUE(resource_type, identifier)
            )
        """)
        print("Table 'rate_limits' recreated with correct schema.")
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_rate_limits_table()
