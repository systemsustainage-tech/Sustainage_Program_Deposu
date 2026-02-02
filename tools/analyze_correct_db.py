import sqlite3
import os

# Correct Local DB Path
DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
OLD_DB_PATH = r'c:\SUSTAINAGESERVER\sustainage.db'

def analyze_db(path, label):
    if not os.path.exists(path):
        print(f"[{label}] Database not found at {path}")
        return

    print(f"\nAnalyzing [{label}] Database: {path}")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Total tables: {len(tables)}")
        print("-" * 60)
        print(f"{'Table Name':<40} | {'Row Count':<10}")
        print("-" * 60)
        
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"{table_name:<40} | {count:<10}")
            except Exception as e:
                print(f"{table_name:<40} | Error: {e}")
                
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing database: {e}")

if __name__ == "__main__":
    analyze_db(DB_PATH, "MAIN")
    analyze_db(OLD_DB_PATH, "OLD/POTENTIAL JUNK")
