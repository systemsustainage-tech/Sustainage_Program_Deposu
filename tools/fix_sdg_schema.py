import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import DB_PATH

def fix_schema():
    print(f"Connecting to {DB_PATH}")
    if not os.path.exists(DB_PATH):
        # Try /var/www/sustainage/data/sdg_desktop.sqlite
        alt_path = "/var/www/sustainage/data/sdg_desktop.sqlite"
        if os.path.exists(alt_path):
            db_path = alt_path
            print(f"Using alternate path: {db_path}")
        else:
            print("Database not found.")
            return
    else:
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check map_sdg_gri table
    try:
        cursor.execute("PRAGMA table_info(map_sdg_gri)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'relation_type' not in columns:
            print("Adding relation_type column to map_sdg_gri...")
            cursor.execute("ALTER TABLE map_sdg_gri ADD COLUMN relation_type TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("relation_type column already exists in map_sdg_gri.")
            
    except Exception as e:
        print(f"Error checking/updating map_sdg_gri: {e}")

    conn.close()

if __name__ == "__main__":
    fix_schema()
