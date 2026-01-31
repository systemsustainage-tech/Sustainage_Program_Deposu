import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_table():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sdg_selections'")
    row = cursor.fetchone()
    
    if row:
        print("Table user_sdg_selections exists.")
        cursor.execute("PRAGMA table_info(user_sdg_selections)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    else:
        print("Table user_sdg_selections DOES NOT exist.")
        
    conn.close()

if __name__ == "__main__":
    check_table()
