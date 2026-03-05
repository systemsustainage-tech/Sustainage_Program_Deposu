import sqlite3
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DB_PATH

def inspect():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Inspecting {DB_PATH}")
    
    tables = ['audit_logs', 'report_templates', 'generated_reports', 'tasks']
    
    for t in tables:
        print(f"\n--- {t} ---")
        cursor.execute(f"PRAGMA table_info({t})")
        rows = cursor.fetchall()
        if not rows:
            print("Table not found.")
        else:
            for r in rows:
                print(r)

    conn.close()

if __name__ == "__main__":
    inspect()
