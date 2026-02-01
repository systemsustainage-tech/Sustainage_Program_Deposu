import sqlite3
import os

db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def check_gri_standards():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gri_standards'")
    if not cursor.fetchone():
        print("Table gri_standards does not exist.")
        return

    # Check columns
    cursor.execute("PRAGMA table_info(gri_standards)")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    print(f"Columns: {col_names}")
    
    if 'effective_date' not in col_names:
        print("MISSING: effective_date")
        # Fix it
        try:
            cursor.execute("ALTER TABLE gri_standards ADD COLUMN effective_date TEXT")
            conn.commit()
            print("ADDED: effective_date column")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("OK: effective_date exists")
        
    conn.close()

if __name__ == "__main__":
    check_gri_standards()
