import sqlite3
import os

DB_PATH = os.path.join("backend", "data", "sdg_desktop.sqlite")

def check_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = ["map_sdg_tsrs", "map_gri_tsrs", "map_sdg_gri"]
    
    print(f"Checking data in {DB_PATH}...")
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"{table}: {count} rows")
            
            if count > 0:
                cur.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cur.fetchall()
                print(f"  Sample data from {table}:")
                for row in rows:
                    print(f"  - {row}")
        except sqlite3.OperationalError as e:
            print(f"Error checking {table}: {e}")

    conn.close()

if __name__ == "__main__":
    check_data()
