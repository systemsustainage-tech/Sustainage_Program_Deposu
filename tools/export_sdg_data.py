import sqlite3
import json
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
OUTPUT_FILE = r"c:\SUSTAINAGESERVER\backend\data\sdg_data_dump.json"

def export_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        data = {}
        tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators', 'sdg_question_bank']
        
        for table in tables:
            print(f"Exporting {table}...")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]
            print(f"  - {len(rows)} records exported.")
            
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Data exported successfully to {OUTPUT_FILE}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    export_data()
