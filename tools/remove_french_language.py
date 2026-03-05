import sqlite3
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DB_PATH

def clean_languages():
    print(f"Checking database at {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='supported_languages'")
        if not cursor.fetchone():
            print("Table 'supported_languages' does not exist.")
            return

        # Check for 'fr'
        cursor.execute("SELECT * FROM supported_languages WHERE language_code = 'fr'")
        rows = cursor.fetchall()
        if rows:
            print(f"Found {len(rows)} entries for 'fr'. Removing...")
            cursor.execute("DELETE FROM supported_languages WHERE language_code = 'fr'")
            conn.commit()
            print("Removed 'fr' from supported_languages.")
        else:
            print("'fr' not found in supported_languages.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_languages()
