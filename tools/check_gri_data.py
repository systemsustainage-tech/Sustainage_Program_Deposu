import sqlite3
import os

DB_PATH = r"C:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_gri_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM gri_standards")
        count = cursor.fetchone()[0]
        print(f"GRI Standards count: {count}")
        
        if count > 0:
            cursor.execute("SELECT code, title, effective_date FROM gri_standards LIMIT 5")
            print("Sample data:")
            for row in cursor.fetchall():
                print(row)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_gri_data()
