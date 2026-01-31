import sqlite3
import os

# Remote path on the server
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_gri_standards():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gri_standards'")
        if not cursor.fetchone():
            print("Table 'gri_standards' does not exist.")
            conn.close()
            return

        # Count rows
        cursor.execute("SELECT COUNT(*) FROM gri_standards")
        count = cursor.fetchone()[0]
        print(f"Row count in gri_standards: {count}")
        
        # Show sample
        if count > 0:
            cursor.execute("SELECT code, title, sector FROM gri_standards LIMIT 5")
            rows = cursor.fetchall()
            print("Sample data:")
            for row in rows:
                print(row)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_gri_standards()
