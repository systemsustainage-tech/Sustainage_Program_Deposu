
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def update_mappings():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create map_sdg_esrs table
        print("Creating map_sdg_esrs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_sdg_esrs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_id INTEGER NOT NULL,
                esrs_code TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(sdg_id) REFERENCES sdg_indicators(id)
            )
        """)
        
        # Verify other mapping tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('map_sdg_gri', 'map_sdg_tsrs')")
        existing = [r[0] for r in cursor.fetchall()]
        print(f"Existing mapping tables: {existing}")
        
        conn.commit()
        print("Mapping tables update completed.")
        
    except Exception as e:
        print(f"Error updating mappings: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_mappings()
