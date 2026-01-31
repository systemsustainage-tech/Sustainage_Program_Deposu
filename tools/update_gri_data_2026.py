import sqlite3
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config.settings import get_db_path
    DB_PATH = get_db_path()
except ImportError:
    # Fallback for direct execution or if config not found
    DB_PATH = '/var/www/sustainage/backend/data/sustainability.db'
    if not os.path.exists(DB_PATH):
        DB_PATH = 'backend/data/sustainability.db'

DATA_FILE = os.path.join(os.path.dirname(__file__), '../backend/data/gri_2026_update.json')

def update_gri_data():
    print(f"Updating GRI data in: {DB_PATH}")
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found: {DATA_FILE}")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure schema
    cursor.execute("PRAGMA table_info(gri_standards)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'sector' not in columns:
        print("Adding 'sector' column...")
        cursor.execute("ALTER TABLE gri_standards ADD COLUMN sector TEXT DEFAULT 'General'")

    if 'updated_at' not in columns:
        print("Adding 'updated_at' column...")
        cursor.execute("ALTER TABLE gri_standards ADD COLUMN updated_at TIMESTAMP")
    
    # Upsert
    for item in data['standards']:
        code = item['code']
        # Check if exists
        cursor.execute("SELECT id FROM gri_standards WHERE code = ?", (code,))
        row = cursor.fetchone()
        
        if row:
            print(f"Updating {code}...")
            cursor.execute("""
                UPDATE gri_standards 
                SET title = ?, category = ?, description = ?, sector = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (item['title_tr'], item['category'], item['description'], item['sector'], row[0]))
        else:
            print(f"Inserting {code}...")
            cursor.execute("""
                INSERT INTO gri_standards (code, title, category, description, sector)
                VALUES (?, ?, ?, ?, ?)
            """, (code, item['title_tr'], item['category'], item['description'], item['sector']))

    conn.commit()
    conn.close()
    print("GRI Data Update Complete.")

if __name__ == "__main__":
    update_gri_data()
