import sqlite3
import os

DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def check_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators', 'sdg_question_bank']
        
        print("--- Table Counts ---")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count}")
            except sqlite3.OperationalError as e:
                print(f"{table}: Error - {e}")
        
        print("\n--- Schema Info ---")
        for table in tables:
            print(f"\nSchema for {table}:")
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                for col in columns:
                    print(col)
            except Exception as e:
                print(f"Error getting schema for {table}: {e}")

        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_data()
