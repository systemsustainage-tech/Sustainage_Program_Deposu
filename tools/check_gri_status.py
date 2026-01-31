import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import get_db_path

def check_gri():
    db_path = get_db_path()
    print(f"Checking DB at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gri_%'")
        tables = cursor.fetchall()
        print("\nGRI Tables found:")
        for t in tables:
            print(f"- {t[0]}")
            
        if not tables:
            print("No GRI tables found.")
            return

        # Check content of gri_standards
        cursor.execute("SELECT COUNT(*) FROM gri_standards")
        count = cursor.fetchone()[0]
        print(f"\nTotal standards in gri_standards: {count}")
        
        # Check indicators for specific standards
        print("\nChecking indicators for GRI 14, GRI 12, GRI 101, GRI 103, GRI 302:")
        target_standards = ['GRI 14', 'GRI 12', 'GRI 101', 'GRI 103', 'GRI 302']
        
        for code in target_standards:
            cursor.execute("SELECT id, title FROM gri_standards WHERE code = ?", (code,))
            std = cursor.fetchone()
            if std:
                std_id, std_title = std
                cursor.execute("SELECT COUNT(*) FROM gri_indicators WHERE standard_id = ?", (std_id,))
                count = cursor.fetchone()[0]
                print(f"{code} ({std_title}): {count} indicators")
                if count > 0:
                    cursor.execute("SELECT code, title FROM gri_indicators WHERE standard_id = ? LIMIT 3", (std_id,))
                    for row in cursor.fetchall():
                        print(f"  - {row[0]}: {row[1]}")
            else:
                print(f"{code}: Not found in gri_standards")
                
    except Exception as e:
        print(f"Error querying GRI data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_gri()
