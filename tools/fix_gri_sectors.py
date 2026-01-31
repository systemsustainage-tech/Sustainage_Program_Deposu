
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import get_db_path

def fix_sectors():
    db_path = get_db_path()
    print(f"Fixing sectors in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define correct sectors
    updates = [
        ('GRI 11', 'Oil & Gas'),
        ('GRI 12', 'Coal'),
        ('GRI 13', 'Agriculture'),
        ('GRI 14', 'Mining'),
        ('GRI 101', 'Biodiversity'), # Technically Environmental but user wants sector specific support
        ('GRI 103', 'Energy')        # Energy 2025
    ]
    
    for code, sector in updates:
        print(f"Updating {code} -> {sector}")
        cursor.execute("UPDATE gri_standards SET sector = ? WHERE code = ?", (sector, code))
        
    conn.commit()
    print("Done.")
    conn.close()

if __name__ == "__main__":
    fix_sectors()
