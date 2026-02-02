import sqlite3
import os
import sys

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')
REMOTE_DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def enable_wal(db_path):
    print(f"Checking WAL mode for: {db_path}")
    if not os.path.exists(db_path):
        print("Database file not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current mode
        cursor.execute("PRAGMA journal_mode;")
        current_mode = cursor.fetchone()[0]
        print(f"Current journal mode: {current_mode}")
        
        if current_mode.lower() != 'wal':
            print("Enabling WAL mode...")
            cursor.execute("PRAGMA journal_mode=WAL;")
            new_mode = cursor.fetchone()[0]
            print(f"New journal mode: {new_mode}")
            
            # Also set synchronous to NORMAL (faster, still safe for WAL)
            cursor.execute("PRAGMA synchronous=NORMAL;")
            print("Set synchronous=NORMAL")
        else:
            print("WAL mode is already enabled.")
            
        conn.close()
        print("Optimization complete.")
        
    except Exception as e:
        print(f"Error optimizing database: {e}")

if __name__ == "__main__":
    # Check if running on remote server via path detection
    if os.path.exists(REMOTE_DB_PATH):
        enable_wal(REMOTE_DB_PATH)
    elif os.path.exists(DB_PATH):
        enable_wal(DB_PATH)
    else:
        # Fallback to local config path if needed
        from config.database import DB_PATH as CONFIG_DB_PATH
        enable_wal(CONFIG_DB_PATH)
